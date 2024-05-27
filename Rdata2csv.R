install.packages("vctrs", repos = "https://cloud.r-project.org/")
install.packages("ggplot2", repos = "https://cloud.r-project.org/")
install.packages("gridExtra", repos = "https://cloud.r-project.org/")
packageVersion("vctrs")
packageVersion("ggplot2")
packageVersion("gridExtra")

# Load the .RData file
load("commDataOrig.Rdata")

# List the objects in the environment
objects <- ls()

# Loop through the objects
for (obj_name in objects) {
  # Check if the object is a data frame
  if (is.data.frame(get(obj_name))) {
    # Write the data frame to a .csv file
    write.csv(get(obj_name), paste0(obj_name, ".csv"))
  }
}