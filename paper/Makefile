
name=genome


all: latexmk

o:
	open $(name).pdf


latexmk:
	latexmk $(name)
	dvipdf $(name)

manual:
	latex $(name)
	bibtex $(name)
	latex $(name)
	pdflatex $(name)

clean:
	rm -f $(name).dvi $(name).bbl $(name).aux $(name).blg $(name).log $(name).fdb_latexmk
