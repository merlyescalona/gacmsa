import argparse,csv,datetime,logging,os, sys, glob, msatools,gacmsa
import numpy as np
from collections  import Counter

NUCLEOTIDES=np.chararray(4, itemsize=1)
NUCLEOTIDES[0]="A";NUCLEOTIDES[1]="C";NUCLEOTIDES[2]="T";NUCLEOTIDES[3]="G"
################################################################################
class GACMSAException(Exception):
	def __init__(self, expression, message, time):
		self.expression = expression
		self.message = message
		self.time= time

################################################################################
class GACMSA:
	inputfile=""
	outputfile=""
	msa=None
	appLogger=None

	def __init__(self, cmdArgs):
		self.appLogger=logging.getLogger("gac-msa")
		self.startime=datetime.datetime.now()
		self.appLogger.info("Start...")
		self.inputfile=os.path.abspath(cmdArgs.input)
		self.outputfile=os.path.abspath(cmdArgs.output)
		if not os.path.exists(self.inputfile):
			raise GACMSAException(False, "Input file does not exist.\nPlease Verify.", datetime.datetime.now()-self.startime)
		if not os.path.exists(os.path.dirname(self.outputfile)):
			raise GACMSAException(False, "Path of the output file does not exist.\nPlease Verify.", datetime.datetime.now()-self.startime)
		self.appLogger.info("Parsing MSA file: {}".format(self.inputfile))
		self.msa=msatools.parseMSAFileWithDescriptions(self.inputfile)

	def calculateAllelicCount(self):
		self.appLogger.info("Calculating Allelic counts")
		sequenceDescriptions=self.msa.keys()
		sequenceSize=0; nSequences=0;
		nSequences=len(sequenceDescriptions)
		for sequence in self.msa:
			sequenceSize=max(sequenceSize,len(self.msa[sequence]))

		matrix=np.chararray((nSequences,sequenceSize), itemsize=1)
		for row in range(0,nSequences):
			key=sequenceDescriptions[row]
			seq=self.msa[key]
			for pos in range(0, sequenceSize):
				matrix[row,pos]=seq[pos]
		self.appLogger.warning("Sequence size: {} and matrix cols: {}".format(sequenceSize,matrix.shape[1]))
		A=np.zeros(sequenceSize); C=np.zeros(sequenceSize);
		T=np.zeros(sequenceSize); G=np.zeros(sequenceSize);
		N=np.zeros(sequenceSize); GAP=np.zeros(sequenceSize);
		TOTAL=np.zeros(sequenceSize)
		for pos in range(0,sequenceSize):
			c=Counter(matrix[:,pos])
			A[pos]=c["A"]
			C[pos]=c["C"]
			T[pos]=c["T"]
			G[pos]=c["G"]
			N[pos]=c["N"]
			GAP[pos]=c["-"]
			if A[pos] > 0: TOTAL[pos]+=1
			if C[pos] > 0: TOTAL[pos]+=1
			if T[pos] > 0: TOTAL[pos]+=1
			if G[pos] > 0: TOTAL[pos]+=1
		return A,C,G,T,N,GAP,TOTAL,nSequences,sequenceSize

	def writeOutput(self, A,C,T,G,N,GAP,TOTAL,NSEQ,SEQSIZE):
		self.appLogger.info("Writing output into: {}".format(self.outputfile))
		numWidth=max(len(str(SEQSIZE)), len(str(NSEQ)))
		with open(self.outputfile, "w") as f:
			f.write("{0:>8}\t{1}\n".format("POSITION","\t".join(["{0:>{1}d}".format(item,numWidth) for item in range(1,SEQSIZE+1)])))
			f.write("{0:>8}\t{1}\n".format("A","\t".join(["{0:>{1}d}".format(int(A[index]),numWidth) for index in range(0,SEQSIZE)])))
			f.write("{0:>8}\t{1}\n".format("C","\t".join(["{0:>{1}d}".format(int(C[index]),numWidth) for index in range(0,SEQSIZE)])))
			f.write("{0:>8}\t{1}\n".format("T","\t".join(["{0:>{1}d}".format(int(T[index]),numWidth) for index in range(0,SEQSIZE)])))
			f.write("{0:>8}\t{1}\n".format("G","\t".join(["{0:>{1}d}".format(int(G[index]),numWidth) for index in range(0,SEQSIZE)])))
			f.write("{0:>8}\t{1}\n".format("N","\t".join(["{0:>{1}d}".format(int(N[index]),numWidth) for index in range(0,SEQSIZE)])))
			f.write("{0:>8}\t{1}\n".format("GAP","\t".join(["{0:>{1}d}".format(int(GAP[index]),numWidth) for index in range(0,SEQSIZE)])))
			f.write("{0:>8}\t{1}\n".format("TOTAL","\t".join(["{0:>{1}d}".format(int(TOTAL[index]),numWidth) for index in range(0,SEQSIZE)])))
			f.write("{0}\t({1})\n".format(NSEQ, SEQSIZE))

	def run(self):
		A,C,T,G,N,GAP,TOTAL, NSEQ,SEQSIZE=self.calculateAllelicCount()
		self.writeOutput(A,C,T,G,N,GAP,TOTAL,NSEQ,SEQSIZE)
		self.appLogger.info("Process finished")
		raise GACMSAException(True, "w", datetime.datetime.now()-self.startime)
