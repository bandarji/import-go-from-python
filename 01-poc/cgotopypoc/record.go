package main

/*
#include <stdint.h>

typedef struct {
	int64_t count;
	double ratio;
	unsigned char ready;
} CRecord;
*/
import "C"
import "unsafe"

type Record struct {
	Count int64
	Ratio float64
	Ready bool
}

func (record Record) cRecord() C.CRecord {
	ready := C.uchar(0)
	if record.Ready {
		ready = 1
	}
	return C.CRecord{
		count: C.int64_t(record.Count),
		ratio: C.double(record.Ratio),
		ready: ready,
	}
}

func recordFromC(raw C.CRecord) Record {
	return Record{
		Count: int64(raw.count),
		Ratio: float64(raw.ratio),
		Ready: raw.ready != 0,
	}
}

//export ReturnRecord
func ReturnRecord() C.CRecord {
	return Record{Count: -7, Ratio: 2.5, Ready: true}.cRecord()
}

//export EchoRecord
func EchoRecord(raw C.CRecord) C.CRecord {
	return recordFromC(raw).cRecord()
}

//export RecordScore
func RecordScore(raw C.CRecord) float64 {
	record := recordFromC(raw)
	if !record.Ready {
		return 0
	}
	return float64(record.Count) * record.Ratio
}

//export RecordSize
func RecordSize() int64 {
	return int64(unsafe.Sizeof(Record{}))
}
