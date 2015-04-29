.. Copyright (C) 2014  Jim Turner

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 2 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.

######
Resume
######

This a system to generate PDF (via LaTeX), HTML, TXT, and Sphinx resumes from a
YAML file containing all of the resume content. It is partly inspired by
`Ming-Ho Yee's resume project <https://github.com/mhyee/resume>`_. A single
Python script performs the transformation using `PyYAML
<http://pyyaml.org/wiki/PyYAML>`_ to parse the data file and `Jinja2
<http://jinja.pocoo.org/>`_ to fill the data into templates.

The primary resume data is stored in ``resume.yml``. A second YAML file
``resume-nonweb.yml`` (not included in this repository) contains information
that should not be publicly available online (address, telephone number,
etc.). ``resume-nonweb.example.yml`` is provided as an example. The Python
script can actually accept arbitrarily many YAML files and merge their data
together.

After parsing the YAML data files, the script applies the regex replacements in
``config.yml`` to the individual strings in the data to escape problematic
characters, apply simple markup, etc. ``config.yml`` also contains configuration
for which delimiters to use for Jinja2 (because the default delimiters don't
work well for LaTeX) and the desired line endings (to enable DOS line endings in
the TXT output for those unfortunate MS Notepad users).

The resulting data is then applied to the various ``*.j2`` templates to generate
the output. The LaTeX output is then compiled to a PDF.

The HTML output is bare-bones, intended for inclusion into a HTML-based blog
with custom CSS. The Sphinx output is a reStructuredText file intended for
inclusion into a `Sphinx`_-based website with custom CSS.

.. _Sphinx: http://sphinx-doc.org/

Usage
=====

To build everything, simply type::

   make

The usage details for the script are::

   usage: transform_resume.py [-h] [--config CONFIG]
                              {latex,html,txt,sphinx} template output data
                              [data ...]

   Render resume templates.

   positional arguments:
     {latex,html,txt,sphinx}
                           Output file type.
     template              Path to Jinja2 template file.
     output                Desired output path.
     data                  Paths to YAML files with data.

   optional arguments:
     -h, --help            show this help message and exit
     --config CONFIG       Path to config YAML file. (default: config.yml)

Dependencies
============

* Python 3.x
* Jinja2
* PyYAML
* LaTeX (for PDF output)

License
=======

See ``LICENSE.rst``.

Contributions
=============

I developed this project for my own personal use. If you have any changes that
would be helpful for general use, please feel free to submit a pull request.
