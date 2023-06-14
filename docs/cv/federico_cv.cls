\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{federico_cv}[6/6/2022 custom CV class]
\LoadClass{article}
\RequirePackage{titlesec}
\usepackage[letterpaper,
            left=1in,
            right=1in,
            top=0.75in,
            bottom=0.75in,
            footskip=.25in]{geometry}
\usepackage{float}
\usepackage[dvipsnames]{xcolor}

\definecolor{dark}{RGB}{0, 0, 0}

\usepackage[colorlinks = true,
            linkcolor = dark,
            urlcolor  = dark,
            citecolor = dark,
            anchorcolor = dark]{hyperref}

\newcommand{\MYhref}[3][dark]{\href{#2}{\color{#1}{#3}}}%

\usepackage{fancyhdr}
 
\pagestyle{fancy}
\fancyhf{}
\lhead{Federico Mora}
\usepackage{lastpage}
\rhead{\thepage/\pageref{LastPage}}
\renewcommand{\headrulewidth}{0pt}
\setlength{\headheight}{0.4in}

\thispagestyle{empty}
\usepackage{multirow}
\usepackage{tabularx}
\newcommand{\contact}[3]{
\vfill\noindent
\begin{tabularx}{\textwidth}{Xr}
  \multirow{2}{*}{\textbf{\huge{#1}}} & #2\\
                                      & #3\\
\end{tabularx}
\vspace{0.5em}
}

\usepackage{longtable}

\titleformat{\section}
  {\large\scshape\raggedright}
  {}{0em}
  {}
  [\titlerule]

\newenvironment{tblSection}[3]
    {\section{#1}
    \vspace{-1.25em}
    \begin{longtable}{@{}p{#2\textwidth} p{#3\textwidth} }
    }
    {
    \end{longtable}
    \vspace{-0.4em}
    }

\newcommand{\leftbfrightsmallleftright}[2]{#1 & \textbf{#2}\\\leftbfrightsmallleftrightCheckNextArg}
\newcommand{\leftbfrightsmallleftrightCheckNextArg}{\@ifnextchar\bgroup{\leftbfrightsmallleftrightGobbleNextArg}{\\[-0.6em]}}
\newcommand{\leftbfrightsmallleftrightGobbleNextArg}[2]{\footnotesize{#1} & #2\\\@ifnextchar\bgroup{\leftbfrightsmallleftrightGobbleNextArg}{\\[-0.6em]}}

\newcommand{\bfsingledash}[1]{\textbf{#1} & \\\bfsingledashCheckNextArg}
\newcommand{\bfsingledashCheckNextArg}{\@ifnextchar\bgroup{\bfsingledashGobbleNextArg}{\\[-0.6em]}}
\newcommand{\bfsingledashGobbleNextArg}[1]{\hspace{\parindent} - #1 & \\\@ifnextchar\bgroup{\bfsingledashGobbleNextArg}{\\[-0.6em]}}

\newcommand{\leftbfrightsingle}[2]{%
    #1 & \textbf{#2} \\\leftbfrightsingleCheckNextArg}
\newcommand{\leftbfrightsingleCheckNextArg}{\@ifnextchar\bgroup{\leftbfrightsingleGobbleNextArg}{\\[-0.6em]}}
\newcommand{\leftbfrightsingleGobbleNextArg}[1]{& #1 \\\@ifnextchar\bgroup{\leftbfrightsingleGobbleNextArg}{\\[-0.6em]}}

\newcommand{\leftrightsingle}[2]{%
    #1 & #2 \\\leftrightsingleCheckNextArg}
\newcommand{\leftrightsingleCheckNextArg}{\@ifnextchar\bgroup{\leftrightsingleGobbleNextArg}{\\[-0.6em]}}
\newcommand{\leftrightsingleGobbleNextArg}[1]{& #1 \\\@ifnextchar\bgroup{\leftrightsingleGobbleNextArg}{\\[-0.6em]}}

\newcommand{\leftrightsingletight}[2]{%
    #1 & #2 \\\leftrightsingletightCheckNextArg}
\newcommand{\leftrightsingletightCheckNextArg}{\@ifnextchar\bgroup{\leftrightsingletightGobbleNextArg}{\\[-1em]}}
\newcommand{\leftrightsingletightGobbleNextArg}[1]{& #1 \\\@ifnextchar\bgroup{\leftrightsingletightGobbleNextArg}{\\[-1em]}}

\newcommand{\leftbfrightsingletight}[2]{%
    #1 & \textbf{#2} \\\leftbfrightsingletightCheckNextArg}
\newcommand{\leftbfrightsingletightCheckNextArg}{\@ifnextchar\bgroup{\leftbfrightsingletightGobbleNextArg}{\\[-1em]}}
\newcommand{\leftbfrightsingletightGobbleNextArg}[1]{& #1 \\\@ifnextchar\bgroup{\leftbfrightsingletightGobbleNextArg}{\\[-1em]}}

\newcommand{\degree}{\leftbfrightsingle}
\newcommand{\job}{\leftbfrightsingle}
\newcommand{\student}{\leftrightsingletight}
\newcommand{\service}{\bfsingledash}
\newcommand{\award}{\leftrightsingletight}
\newcommand{\grant}{\leftbfrightsingle}