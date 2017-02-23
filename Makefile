# Copyright (C) 2014  Jim Turner
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

.PHONY: default nonweb web

default: resume.pdf resume-web.pdf resume-blog.html resume-sphinx.rst resume.txt resume-web.txt

nonweb: resume.pdf resume.txt

web: resume-web.pdf resume-blog.html resume-web.txt

resume.tex: resume.tex.j2 transform_resume.py config.yml resume.yml resume-nonweb.yml
	python3 transform_resume.py latex $< $@ resume.yml resume-nonweb.yml

resume-web.tex: resume.tex.j2 transform_resume.py config.yml resume.yml
	python3 transform_resume.py latex $< $@ resume.yml

resume.pdf: resume.tex moderncvcolorbluecustom.sty moderncvstylebankingcustom.sty
	latexmk -pdf $<

resume-web.pdf: resume-web.tex moderncvcolorbluecustom.sty moderncvstylebankingcustom.sty
	latexmk -pdf $<

resume-blog.html: resume-blog.html.j2 transform_resume.py config.yml resume.yml
	python3 transform_resume.py html $< $@ resume.yml

resume.txt: resume.txt.j2 transform_resume.py config.yml resume.yml resume-nonweb.yml
	python3 transform_resume.py txt $< $@ resume.yml resume-nonweb.yml

resume-web.txt: resume.txt.j2 transform_resume.py config.yml resume.yml
	python3 transform_resume.py txt $< $@ resume.yml

resume-sphinx.rst: resume-sphinx.rst.j2 transform_resume.py config.yml resume.yml
	python3 transform_resume.py sphinx $< $@ resume.yml

clean:
	rm -f -- *.aux *.fls *.fdb_latexmk *.log *.out resume*.txt resume*.html resume*.pdf resume*.tex resume*.rst
	rm -rf -- auto/
