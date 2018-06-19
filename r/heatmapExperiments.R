sampleData <- scan("/Users/a_s899/Sasha/Dropbox/code/r/sampleData.csv", what=list("integer","integer"), sep=",", nmax=500)	# this reas them as string

sampleData[[1]][1]

hist(as.integer(sampleData[[1]]), breaks=100)
hist(as.integer(sampleData[[1]]), breaks=100, col="grey90", border=NA)

# or

sampleData <- scan("/Users/a_s899/Sasha/Dropbox/code/r/sampleData.csv", what=list(integer(),integer()), sep=",", nmax=500)	# this reads them as ints

hist(as.integer(sampleData[[1]]), breaks=100, col="grey90", border=NA)


# next step - aggregate into 2D bins


# 12+13 = right eye x+y, 27+28 = left eye x+y
# 8+23 = right+left validity

sampleData <- scan("/Users/a_s899/Sasha/Dropbox/code/r/gazeData.clean.out", what=list(NULL, NULL, NULL, NULL, NULL, NULL, NULL, integer(), NULL, NULL, NULL, numeric(), numeric(), NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, integer(), NULL, NULL, NULL, numeric(), numeric(), NULL, NULL, NULL, NULL), sep="\t", nmax=400)

nbins <- 10

# seq(floor(min(sampleData[[12]])), ceiling(max(sampleData[[13]])), length=10)
bins <- seq(0, 1, length=nbins) # it's always this for eye tracking data

freq <-  as.data.frame(table(findInterval(sampleData[[12]], bins), findInterval(sampleData[[13]], bins)))
# findInterval assigns NaN to NA, creating an alternative 
freq[,1] <- as.numeric(freq[,1])
freq[,2] <- as.numeric(freq[,2])

freq2D <- diag(nbins)*0
freq2D[cbind(freq[,1], freq[,2])] <- freq[,3]

par(mfrow=c(1,2))
image(bins, bins, freq2D, col=topo.colors(max(freq2D)))




# skip first line (header)
# process "nan":
# 	"NaN" is considered allowed input for a numeric field, and is parsed in a case-insensitive fashion
#	NaN itself is a numeric constant of type double
sampleData <- scan("/Users/a_s899/Sasha/Dropbox/code/r/gazeData.2018.05.08.at.12.13.25.out", sep="\t", nmax=160000, skip=1, what=list(NULL, NULL, NULL, NULL, NULL, NULL, NULL, integer(), NULL, NULL, NULL, numeric(), numeric(), NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, integer(), NULL, NULL, NULL, numeric(), numeric(), NULL, NULL, NULL, NULL))



nbins <- 100

bins <- seq(0, 1, length=nbins)

freq2D <- diag(nbins)*0

numRec <- length(sampleData[[8]])

for (i in 1:numRec) {

	leftValid	<- as.logical(sampleData[[23]][i]);
	rightValid	<- as.logical(sampleData[[8]][i]);

	if (leftValid && rightValid) {

		# right eye
		xBin <- findInterval(sampleData[[12]][i], bins);
		yBin <- findInterval(1 - sampleData[[13]][i], bins);

		freq2D[xBin, yBin] <- freq2D[xBin, yBin] + 1;
	}
}

library(RColorBrewer)

par(bg="grey90") # needed every time
image(bins, bins, freq2D, zlim=c(1, max(freq2D)), col=brewer.pal(9, "Blues")) # exclude cells with 0 count or just suppress for plotting?



# build a histogram over the matrix counts
# use it to produce a "breaks" parameter for the image() function


hist(freq2D, breaks=100, col="grey90", border=NA, plot=FALSE)

hist(freq2D, breaks=seq(from=1, to=max(freq2D), by=50), col="grey90", border=NA, plot=FALSE)
Error in hist.default(freq2D, breaks = seq(from = 1, to = max(freq2D),  : 
  some 'x' not counted; maybe 'breaks' do not span range of 'x'

















