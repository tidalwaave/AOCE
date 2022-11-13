from math import dist

class Vector():
	"""2D Custom Vector Class"""

	def __init__(self, x=0, y=0):
		"""Initializer of a vector"""
		self.x = x
		self.y = y

	def __str__(self):
		"""Improving the view when printing a vector"""
		return f"Vector({self.x}, {self.y})"

	def __add__(self, other):
		"""Addition"""
		return Vector(self.x + other.x, self.y + other.y) if isinstance(other, Vector) else NotImplemented

	def __sub__(self, other):
		"""Substraction"""
		return Vector(self.x - other.x, self.y - other.y) if isinstance(other, Vector) else NotImplemented

	def __mul__(self, other):
		"""Scalar Product / Multiplying a vector by a real"""
		if isinstance(other, Vector):
			return self.x * other.x + self.y * other.y
		if isinstance(other, (int, float)):
			return Vector(self.x * other, self.y * other)
		return NotImplemented

	def __rmul__(self, other):
		"""Multiplication of a vector with an int on both side"""
		return self.__mul__(other)

	def __truediv__(self, other):
		"""Dividing a vector by a real"""
		return Vector(self.x / other, self.y / other) if isinstance(other, (int, float)) else NotImplemented

	def __floordiv__(self, other):
		"""Dividing a vector by a real"""
		return Vector(self.x // other, self.y // other) if isinstance(other, (int, float)) else NotImplemented

	def __eq__(self, other):
		"""Equality between vectors"""
		return self.x == other.x and self.y == other.y if isinstance(other, Vector) else NotImplemented

	def __pos__(self):
		"""+Vector"""
		return self

	def __neg__(self):
		"""Negation of a Vector"""
		return Vector(-self.x, -self.y)

	def __iter__(self):
		"""Iterator built from a vector. Enables Vector to Tuple conversion"""
		for i in (self.x, self.y):
			yield i

	def norm(self):
		"""Norm of the vector"""
		return dist((0, 0), (self.x, self.y))

	def normalized(self):
		"""Normalize the vector: Convert a vector into a unit vector."""
		return self / self.norm()

	def isalmost(self, other, d=5):
		"""Tests if vectors n and m are close with a maximum distance of d"""
		return (self - other).norm() < d

	def int(self):
		return Vector(int(self.x), int(self.y))

	def round(self):
		return Vector(round(self.x), round(self.y))
