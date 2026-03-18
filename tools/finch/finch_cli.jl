#!/home/ubuntu/.juliaup/bin/julia

using SparseArrays
using LinearAlgebra
using MatrixMarket
using HDF5
using JSON
using Finch

const TYPE_TO_BINSPARSE = Dict{DataType,String}(
    Bool => "bint8",
    Int8 => "int8",
    Int16 => "int16",
    Int32 => "int32",
    Int64 => "int64",
    UInt8 => "uint8",
    UInt16 => "uint16",
    UInt32 => "uint32",
    UInt64 => "uint64",
    Float32 => "float32",
    Float64 => "float64",
)

function usage()
    println("usage:")
    println("  finch_cli.jl mtx2bsp INPUT.mtx OUTPUT.bsp.h5")
    println("  finch_cli.jl bsp2mtx INPUT.bsp.h5 OUTPUT.mtx")
    println("  finch_cli.jl check_equivalence FILE1 FILE2")
    return 1
end

function binsparse_type_name(::Type{Complex{T}}) where {T}
    return "complex[$(binsparse_type_name(T))]"
end

function binsparse_type_name(T::Type)
    haskey(TYPE_TO_BINSPARSE, T) || error("unsupported binsparse element type: $T")
    return TYPE_TO_BINSPARSE[T]
end

function best_index_type(limit::Integer)
    if limit <= typemax(UInt8)
        return UInt8
    elseif limit <= typemax(UInt16)
        return UInt16
    elseif limit <= typemax(UInt32)
        return UInt32
    else
        return UInt64
    end
end

function matrix_from_mtx(path::AbstractString)
    raw = mmread(path)
    return sparse(raw)
end

function binsparse_values_dataset(desc, raw_values)
    value_type = desc["data_types"]["values"]
    nnz = Int(desc["number_of_stored_values"])

    if startswith(value_type, "iso[")
        inner_name = match(r"^iso\[(.*)\]$", value_type).captures[1]
        inner_type = binsparse_scalar_type(inner_name)
        value = convert(inner_type, raw_values[1])
        return fill(value, nnz)
    end

    if startswith(value_type, "complex[")
        inner_name = match(r"^complex\[(.*)\]$", value_type).captures[1]
        inner_type = binsparse_scalar_type(inner_name)
        return reinterpret(Complex{inner_type}, raw_values)
    end

    return raw_values
end

function binsparse_scalar_type(name::AbstractString)
    lookup = Dict(
        "bint8" => Bool,
        "int8" => Int8,
        "int16" => Int16,
        "int32" => Int32,
        "int64" => Int64,
        "uint8" => UInt8,
        "uint16" => UInt16,
        "uint32" => UInt32,
        "uint64" => UInt64,
        "float32" => Float32,
        "float64" => Float64,
    )
    haskey(lookup, name) || error("unsupported binsparse scalar type: $name")
    return lookup[name]
end

function matrix_from_bsp(path::AbstractString)
    h5open(path, "r") do file
        metadata = JSON.parse(read(attributes(file)["binsparse"]))
        desc = metadata["binsparse"]
        format = desc["format"]
        format == "COO" || error("unsupported binsparse format in Finch adapter: $format")

        shape = Tuple(Int.(desc["shape"]))
        structure = get(desc, "structure", "general")

        row = Int.(read(file["indices_0"])) .+ 1
        col = Int.(read(file["indices_1"])) .+ 1
        raw_values = read(file["values"])
        values = binsparse_values_dataset(desc, raw_values)

        if startswith(structure, "symmetric")
            mirror_row = Int[]
            mirror_col = Int[]
            mirror_values = eltype(values)[]
            for (r, c, v) in zip(row, col, values)
                if r != c
                    push!(mirror_row, c)
                    push!(mirror_col, r)
                    push!(mirror_values, v)
                end
            end
            append!(row, mirror_row)
            append!(col, mirror_col)
            append!(values, mirror_values)
        else
            structure == "general" || error(
                "unsupported binsparse structure in Finch adapter: $structure",
            )
        end

        return sparse(row, col, values, shape...)
    end
end

function matrix_from_file(path::AbstractString)
    if endswith(path, ".mtx")
        return SparseMatrixCSC(Tensor(matrix_from_mtx(path)))
    elseif endswith(path, ".bsp.h5") || endswith(path, ".bsp.hdf5")
        return SparseMatrixCSC(Tensor(matrix_from_bsp(path)))
    else
        error("unsupported input format: $path")
    end
end

function write_bsp(path::AbstractString, matrix::SparseMatrixCSC)
    tensor = Tensor(matrix)
    canonical = SparseMatrixCSC(tensor)
    row, col, values = findnz(canonical)
    index_type = best_index_type(max(size(canonical)...))
    row_data = convert.(index_type, row .- 1)
    col_data = convert.(index_type, col .- 1)

    data_types = Dict(
        "indices_0" => binsparse_type_name(index_type),
        "indices_1" => binsparse_type_name(index_type),
        "values" => binsparse_type_name(eltype(values)),
    )

    header = JSON.json(
        Dict(
            "binsparse" => Dict(
                "version" => "0.1",
                "format" => "COO",
                "shape" => collect(size(canonical)),
                "number_of_stored_values" => length(values),
                "data_types" => data_types,
            ),
        ),
        4,
    )

    h5open(path, "w") do file
        attributes(file)["binsparse"] = header
        file["indices_0"] = row_data
        file["indices_1"] = col_data
        file["values"] = values
    end

    return path
end

function write_mtx(path::AbstractString, matrix::SparseMatrixCSC)
    mmwrite(path, matrix)
    return path
end

function do_mtx2bsp(input_path::AbstractString, output_path::AbstractString)
    write_bsp(output_path, matrix_from_mtx(input_path))
end

function do_bsp2mtx(input_path::AbstractString, output_path::AbstractString)
    write_mtx(output_path, matrix_from_bsp(input_path))
end

function do_check_equivalence(path1::AbstractString, path2::AbstractString)
    matrix1 = matrix_from_file(path1)
    matrix2 = matrix_from_file(path2)

    if size(matrix1) != size(matrix2)
        println(stderr, "dimension mismatch: $(size(matrix1)) != $(size(matrix2))")
        return 1
    end

    if matrix1 != matrix2
        println(stderr, "matrices are not equivalent")
        return 2
    end

    println("The files are equivalent.")
    println("OK!")
    return 0
end

function main(args)
    length(args) == 3 || return usage()
    command, arg1, arg2 = args

    if command == "mtx2bsp"
        do_mtx2bsp(arg1, arg2)
        return 0
    elseif command == "bsp2mtx"
        do_bsp2mtx(arg1, arg2)
        return 0
    elseif command == "check_equivalence"
        return do_check_equivalence(arg1, arg2)
    else
        return usage()
    end
end

exit(main(ARGS))
