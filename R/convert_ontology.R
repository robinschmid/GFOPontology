#' Convert ontology to data frame
#'
#' @importFrom ontologyIndex get_ontology
#' @importFrom  rlang is_empty
#' @importFrom  plyr mapvalues
#' @import tidyverse
#' @param obo_file Path to ontology file with .obo extension.
#' @param save_name Path to save data frame with .txt extension.
#' @return A data frame where each row contains the full lineage for an ontology term
#' @export

convert_onto <- function(obo_file, save_name) {
  ont <- get_ontology(obo_file)
  # get terminal leaves
  leaves <- unname(ont$id[unlist(lapply(ont$children, function(x) {is_empty(x)}))])
  # get direct parents
  parents <- unlist(ont$parents[names(ont$parents) %in% leaves])
  gfop <- data.frame(leaf = names(parents), parent1 = unname(parents))
  i <- 1
  parents <- unlist(ont$parents[names(ont$parents) %in% gfop[[paste0("parent", i)]]])
  while (!is_empty(parents)) {
    hold <- data.frame(names(parents), unname(parents))
    colnames(hold) <- c(paste0("parent", i), paste0("parent", i+1))
    gfop <- full_join(gfop, hold, by = paste0("parent", i))
    i <- i+1
    parents <- unlist(ont$parents[names(ont$parents) %in% gfop[[paste0("parent", i)]]])
  }
  # change term IDs to names
  gfop <- mutate_all(gfop, ~mapvalues(., from = names(ont$name), to = unname(ont$name), warn_missing = FALSE))
  write_delim(gfop, save_name, delim = "\t")
  return(gfop)
}


#' Generate foodMASST input
#'
#' Link all food filenames to each level of ontology
#'
#' @import tidyverse
#' @import magrittr
#' @param ont Ontology data frame generated by `convert_onto()`.
#' @param meta_file Path to food metadata file.
#' @param save_name Path to save foodMASST file with .txt extension.
#' @export

generate_foodmasst_file <- function(ont, meta_file, save_name) {
  meta <- read_delim(meta_file, delim = "\t", guess_max = 3000)
  # convert ontology to long format (each ontology term needs to be a leaf with its parents in subsequent columns)
  ont_df <- rbind(ont,
                  ont %>%
                    dplyr::select(-leaf) %>%
                    filter(!duplicated(parent1)) %>%
                    mutate(parent8 = NA) %>%
                    set_colnames(colnames(ont))) %>%
    filter(!duplicated(leaf)) %>%
    rbind(ont %>%
            dplyr::select(-leaf, -parent1) %>%
            filter(!duplicated(parent2)) %>%
            mutate(parent8 = NA, parent9 = NA) %>%
            set_colnames(colnames(ont))) %>%
    filter(!duplicated(leaf))
  # include complex at L1
  ont_df$leaf <- replace_na(ont_df$leaf, "complex")
  # attach filenames to ontology
  ont_filenames <- right_join(ont_df, select(meta, filename, ontology_terminal_leaf), by = c("leaf" = "ontology_terminal_leaf")) %>%
  # long format - for every file, list all associated ontology terms
    pivot_longer(!filename, values_to = "ontology_term") %>%
    dplyr::select(-name) %>%
    filter(!is.na(ontology_term))
  write_delim(ont_filenames, save_name, delim = "\t")
}
