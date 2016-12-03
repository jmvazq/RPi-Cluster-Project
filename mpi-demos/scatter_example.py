from mpi4py import MPI

comm = MPI.COMM_WORLD

size = comm.size
rank = comm.rank
if rank == 0: 
	data = [(x+1) ** x for x in range (size)]
	print 'scattering data: ',data
else:
	data = None
data = comm.scatter(data,root=0)
print 'rank ',rank,' has data: ', data
