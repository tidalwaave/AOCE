from vector import Vector


def test():
	v = Vector(2, 3)
	w = Vector(4, 5)
	z = Vector(2.8, -6.7)
	unit = Vector(1, 1)
	print(v)
	print(v.x)
	print(v.y)
	print(w)
	print(v + w)
	print(z)
	print(+z)
	print(-z)
	print(v * 5)
	print(tuple(v))
	print(v / 2)
	print(v * 2)
	print(2 * v)
	print(v * unit)
	print(v.normalized())
	print(v == Vector(2, 3))
	print(v == Vector(2, 4))
	print(v != Vector(2, 4))
	print(v != Vector(2, 3))


if __name__ == "__main__":  # Python syntax that means "if you are launching from this file, run main()", useful if this file is going to be imported.
	test()
