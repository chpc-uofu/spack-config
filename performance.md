# Performance observations on Zen2 and SKL with different uarch optimized Spack built binaries

## Gromacs

Gromacs was picked because it is among a few Spack recipes that has explicit uarch directives.

### Observations:

- Spack built uarch optimized binaries provide best results
- hyperthreading helps
- for Zen2, use the SandyBridge binary, not Zen2

All results for benchMEM, ns/day = higher is better

1. Load balance on and auto pinning is the most performant (those should be the defaults, or -dlb yes -pin auto)

2. uarch optimized binaries are important, esp. for SKL:

Zen2 64 CPU cores, HT off	
			
|CPU	|Nehalem	|SandyBridge	|Zen2		|Skylake|
|uarch	|SSE4.2, HT	|AVX, HT	|AVX2, no HT	|AVX512|
|ns/day	|72.26		|87.12		|78.91		|N/A|

SKL 32 CPU cores, HT on				
CPU	Nehalem	SandyBridge	Zen2	Skylake
uarch	SSE4.2	AVX		AVX2	AVX512
ns/day	35.89	41.58		44.19	51.65

3. Hyperthreading slower on Zen2 with Zen2 optimized binary, faster with Intel optimized binaries:

Zen 2 HT comparison				
	Nehalem	SandyBridge	Zen2 MKL	Zen 2 OB
HT	72.26	87.12		76.44		76.00
no HT	67.24	85.07		78.91		70.98

SKL HT comparison				
	Nehalem	SandyBridge	Zen2 MKL	Zen 2 OB
HT	35.89	41.58	44.19	51.65
no HT	33.93	38.46	42.61	48.87

4. OpenBLAS is slower than MKL on Zen2, but, close when HT is on

5. Parallel scaling is about the same on Zen2 and SKL columns 8, 16, 32, 64 cores:
Zen2:
8	16	32	64
1	2	4	8
1.00	1.85	2.98	4.12
SKL:
8	16	32
1	2	4
1.00	1.81	2.79

6. MKLs LD_PRELOAD helps on Zen2:

LD_PRELOAD comparison, SandyBridge	
off	on
83.90	85.07

### Recomendation

Build 3 binaries, nehalem, sandybridge and skylake_avx512
For Zen2 use sandybridge binary
Hardcode libfakeintel.so into the sandybridge binary
```
/uufs/chpc.utah.edu/sys/installdir/amdmkl/bin/patchmkl.sh /uufs/chpc.utah.edu/sys/spack/linux-centos7-sandybridge/gcc-10.2.0/gromacs-2020.4-e6jluwefhuwdbcwctqp2gfdiepkh3jsg/bin/gmx_mpi
```

### Installation
```
spack install gromacs%gcc@10.2.0+lapack^intel-mkl threads=openmp target=nehalem
spack install gromacs%gcc@10.2.0+lapack^intel-mkl threads=openmp target=sandybridge
spack install gromacs%gcc@10.2.0+lapack^intel-mkl threads=openmp target=skylake_avx512
```

## NWCHEM

NWCHEM was selected because it is expected to heavily utilize accelerated linear algebra.

Runtime in seconds, lower is better.

### Observations

1. uarch optimized binaries have small effect on execution time (7% on zen2, 5% on skl wrt. nehalem build)

2. MKL is not being used much since LD_PRELOAD trick does not have any effect on runtime.

uarch binary	nehalem	nehldpreload	sb	sbldpreload	skl	sklldpreload	zen2	zen2ldpreload
zen2 node	1162	1156		1086	1089		1112	1142		1112	1142
skl node	2201			2235			2098			2189	

### Recomendation

Build 3 binaries, nehalem, sandybridge and skylake-avx512
For Zen2 use sandybridge binary
No need to do anything with LD_PRELOAD

## Quantum Espresso

QE is also expected to have strong linear algebra dependency


Runtime in seconds, lower is better.

### Observations:

1. uarch optimized binaries have no effect on the Zen2 and about 5% improvement on SB and SKL over NEH

2. LD_PRELOAD has a huge effect on the performance, which suggests that most of time is spent in the MKL routines

		nehalem	nehldpreload	sb	sbldpreload	skl	sklldpreload
zen2_node	718	378		715	377		714	377
skl_node	467			442	443		444	

### Recomendation

Build binaries, nehalem, sandybridge
For Zen2 use sandybridge binary
Hardcode libfakeintel.so into the sandybridge binary
```
for i in `ls /uufs/chpc.utah.edu/sys/spack/linux-centos7-sandybridge/gcc-8.3.0/quantum-espresso-6.6-nbtlug57rby5ejjinegl62ak4uagpmpj/*.x`; do /uufs/chpc.utah.edu/sys/installdir/amdmkl/bin/patchmkl.sh $i; done
```

### Installation
```
spack install quantum-espresso+openmp+epw+elpa hdf5=parallel ^intel-mkl threads=openmp target=nehalem
spack install quantum-espresso+openmp+epw+elpa hdf5=parallel ^intel-mkl threads=openmp target=sandybridge
```
