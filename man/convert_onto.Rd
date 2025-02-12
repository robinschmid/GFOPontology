% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/convert_ontology.R
\name{convert_onto}
\alias{convert_onto}
\title{Convert ontology to data frame}
\usage{
convert_onto(obo_file, save_name)
}
\arguments{
\item{obo_file}{Path to ontology file with .obo extension.}

\item{save_name}{Path to save data frame with .txt extension.}
}
\value{
A data frame where each row contains the full lineage for an ontology term
}
\description{
Convert ontology to data frame
}
