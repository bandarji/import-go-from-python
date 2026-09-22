// Package main is compiled as a C shared library so Python can import
// the exported functions through ctypes.
package main

/*
#include <stdlib.h>

typedef struct {
	float real;
	float imag;
} CPyComplex64;

typedef struct {
	double real;
	double imag;
} CPyComplex128;
*/
import "C"

import "unsafe"

//export ReturnNone
func ReturnNone() unsafe.Pointer {
	return nil
}

//export ReturnBoolTrue
func ReturnBoolTrue() bool {
	return true
}

//export ReturnBoolFalse
func ReturnBoolFalse() bool {
	return false
}

//export ReturnInt8
func ReturnInt8() int8 {
	return -128
}

//export ReturnInt16
func ReturnInt16() int16 {
	return -32768
}

//export ReturnInt32
func ReturnInt32() int32 {
	return -2147483648
}

//export ReturnInt64
func ReturnInt64() int64 {
	return -9223372036854775808
}

//export ReturnUint8
func ReturnUint8() uint8 {
	return 255
}

//export ReturnUint16
func ReturnUint16() uint16 {
	return 65535
}

//export ReturnUint32
func ReturnUint32() uint32 {
	return 4294967295
}

//export ReturnUint64
func ReturnUint64() uint64 {
	return 18446744073709551615
}

//export ReturnFloat32
func ReturnFloat32() float32 {
	return 1.5
}

//export ReturnFloat64
func ReturnFloat64() float64 {
	return 2.718281828459045
}

//export ReturnComplex64
func ReturnComplex64() C.CPyComplex64 {
	return C.CPyComplex64{real: 1.5, imag: -2.5}
}

//export ReturnComplex128
func ReturnComplex128() C.CPyComplex128 {
	return C.CPyComplex128{real: 1.25, imag: -2.5}
}

//export ReturnString
func ReturnString() *C.char {
	return C.CString("hello from go")
}

//export ReturnEmptyString
func ReturnEmptyString() *C.char {
	return C.CString("")
}

//export ReturnUnicodeString
func ReturnUnicodeString() *C.char {
	return C.CString("बंदरजी")
}

//export ReturnBytes
func ReturnBytes(n *C.int) *C.char {
	data := []byte{0x00, 0x7f, 0x80, 0xff}
	*n = C.int(len(data))
	return (*C.char)(C.CBytes(data))
}

//export FreeCString
func FreeCString(p *C.char) {
	C.free(unsafe.Pointer(p))
}

func main() {}
