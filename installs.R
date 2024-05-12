install.packages("vctrs", repos = "https://cloud.r-project.org/")
install.packages("ggplot2", repos = "https://cloud.r-project.org/")
install.packages("gridExtra", repos = "https://cloud.r-project.org/")
packageVersion("vctrs")
packageVersion("ggplot2")
packageVersion("gridExtra")


# Load the data from the CSV file
data <- read.csv("CommDataSyn.csv")

# Save the data frame as an RData file
save(data, file = "CommDataSyn.Rdata")