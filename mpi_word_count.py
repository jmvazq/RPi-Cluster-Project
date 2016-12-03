from mpi4py import MPI
import more_itertools
from timeit import default_timer as timer
import itertools 

# The comm object we use to get information about the processes/nodes
comm = MPI.COMM_WORLD
# Rank refers to the node's number, id, whatever...
rank = comm.Get_rank()
size = comm.Get_size()

# Our Word Count function
def wordcount(data):
	dict = {}
	for word in data:
	   	if word not in dict: dict[word] = 1
   		else: dict[word] += 1
	unique = dict.keys()
	return dict

# Chunking function (borrowed from StackOverflow, OK?!)
# Used to divide book into n chunks, where n = number of nodes executing
def chunkIt(seq, num):
  avg = len(seq) / float(num)
  out = []
  last = 0.0

  while last < len(seq):
    out.append(seq[int(last):int(last + avg)])
    last += avg

  return out

# Prepare our Word Count data chunks
text = {}
chunks = {}

if rank == 0:
	# File to save results to
	writtenfile = open('results.txt','r+')
	# List of books we can read from
	books = ['books/Bibble.txt', 'books/MSFrankenstein.txt', 'books/DonQuijote.txt', 'books/Odyssey.txt']
	# Ask for book to read from:
	print "Select the book to read:"
	print "0 - The Holy Bible    1 - Frankenstein    2 - Don Quixote    3 - The Odyssey"
	booknum = int(raw_input("Enter number: "))

	# Extract contents of book
	text = open(books[booknum],'r').read()
	# cleanup the text before splitting
	text = text.translate(None,'*%^!@#$-}{,.!?_;:/\)("\'`1234567890')
	words = text.split()
	chunks = chunkIt(words, size)

# Once the data we need is ready to distribute, we use MPI to do it

# Master node is rank 0 by default
# Only Master node has the data, so there is no Fault Tolerance here
if rank == 0:
    data = chunks
else:
    data = None

# Start tracking time
start = timer()

# The data we scattered (distributed) to each node
scattered = comm.scatter(data, root=0)

# The data after each node has processed it by executing wordcount()
gathered = comm.gather(wordcount(scattered), root=0)

# Once we have received the processed data from the nodes, we need to process it for presentation and use

# Merge all chunks back into one big chunk of data
if rank == 0:
	merged = {}
	for dict in gathered:
		if dict is not None:
			merged.update(dict)

	# Sort the big chunk of data alphabetically
	sorted = merged.keys()
	sorted.sort()

	print "Saving results to results.txt"
	# Save output to a file
	for word in sorted:
		writtenfile.write(word + " - " + str(merged[word]) + '\n')

	# End tracking time
	end = timer()

	print(str(end - start) + " seconds elapsed with " + str(size) + " nodes.")

	# Close file stream
	writtenfile.close()


