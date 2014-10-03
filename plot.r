
require(ggplot2)

dat = read.table('matchresults.txt', sep='\t')

df = data.frame(x=dat$V6, y=dat$V5, names=dat$V2)

ggplot(df, aes(x,y)) + geom_text(aes(label=names)) + ylab("Total Matched Base Pairs") +xlab("Total Base Pairs") + ggtitle("Total Base Pairs vs. Total Matched Base Pairs for Viral Sequences Aligned to Human Genome")

