proc scss_reset {} {
	irscan firestarter.cltap 0x34; drscan firestarter.cltap 1 0x1
	irscan firestarter.cltap 0x32; drscan firestarter.cltap 32 0x00000008
	irscan firestarter.cltap 0x31; drscan firestarter.cltap 16 0x8570
	irscan firestarter.cltap 0x31; drscan firestarter.cltap 16 0x0
	irscan firestarter.cltap 0x34; drscan firestarter.cltap 1 0x0
	reset
}

