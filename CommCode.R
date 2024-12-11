#B. Lesko�ek, 2024-04-25.
#for B. Francis, synDiffix
#code used for paper https://link.springer.com/content/pdf/10.1186/s12889-021-10326-6.pdf

# Total columns: "VO2max","CommToSch","CommHome","gender","age","MVPAsqrt","DistLogToHome","DistLogToSch","DistFromHome","DistFromSchool"

runComputation <- function(commDataPath2Sch, commDataPath2Home, dataPath, plotPath) {
    library(ggplot2)
    library(cowplot)

    dd2s <- read.csv(commDataPath2Sch)
    # If dd2s$DistFromHome is in dd2s, the convert it to log
    if ("DistFromHome" %in% colnames(dd2s)) {
        print("Do the transformation for DistFromHome")
        dd2s$DistLogToSch <- log2(dd2s$DistFromHome)
    }
    dd2s$CommToSch = factor(dd2s$CommToSch, levels=c('car', 'public', 'wheels', 'walk'))
    dd2s$gender = factor(dd2s$gender, levels=c('male', 'female'))
    dd2s <- within(dd2s, gender <- relevel(gender, ref = 2))
    dd2s <- within(dd2s, CommToSch <- relevel(CommToSch, ref = 4))

    dd2h <- read.csv(commDataPath2Home)
    if ("DistFromSchool" %in% colnames(dd2h)) {
        print("Do the transformation for DistFromSchool")
        dd2h$DistLogToHome <- log2(dd2h$DistFromSchool)
    }
    dd2h$CommHome = factor(dd2h$CommHome, levels=c('car', 'public', 'wheels', 'walk'))
    dd2h$gender = factor(dd2h$gender, levels=c('male', 'female'))
    dd2h <- within(dd2h, gender <- relevel(gender, ref = 2))
    dd2h <- within(dd2h, CommHome <- relevel(CommHome, ref = 4))

    ### from Home 2 Sch
    m=lm(VO2max ~ CommToSch*gender + age + MVPAsqrt + DistLogToSch:CommToSch , data=dd2s)
    summary(m)
    summ <- summary(m)
    conf_int <- confint(m, level = 0.95)
    df2s <- as.data.frame(conf_int)
    df2s <- na.omit(df2s)
    if (nrow(df2s) == nrow(summ$coefficients)) {
        # If they match, proceed to assign
        df2s$Estimate <- summ$coefficients[, "Estimate"]
        df2s$Std.Error <- summ$coefficients[, "Std. Error"]
        df2s$t.value <- summ$coefficients[, "t value"]
        df2s$Pr.t. <- summ$coefficients[, "Pr(>|t|)"]
      } else {
        # If they don't match, print a warning or handle the discrepancy
        warning("Home 2 Sch Mismatch in number of coefficients and confidence intervals. Check model specification.")
        # Output the contents of df2s and summ$coefficients
        print("Contents of df2s (Confidence Intervals):")
        print(df2s)
        print("Contents of summ$coefficients:")
        print(summ$coefficients)
        # Optional: Handle the discrepancy, e.g., by aligning the rows or investigating the cause
      }
    library(jsonlite)
    new <- data.frame(gender=c(rep(1,4), rep(2,4)), CommToSch=0:3, age=mean(dd2s$age), MVPAsqrt=mean(dd2s$MVPAsqrt),
                    DistLogToSch=aggregate(dd2s[, "DistLogToSch"], list(dd2s$CommToSch), median)$x)
    new$gender= factor(new$gender);  levels(new$gender)=levels(dd2s$gender)
    new$CommToSch= factor(new$CommToSch);  levels(new$CommToSch)=levels(dd2s$CommToSch)
    new$CommToSch = factor(new$CommToSch,levels(dd2s$CommToSch)[c(1,2,4,3)])
    Ypred= predict.lm(m, new)
    #zzzz pred.w.plim <- predict(m, new, interval = "prediction")
    pred.w.clim <- predict(m, new, interval = "confidence")
    pd <- position_dodge(0.3) # move them .05 to the left and right
    q=cbind(new, pred.w.clim)
    q$CommToSch <- factor(q$CommToSch, levels = c("car", "public", "walk", "wheels"))
    q$gender <- factor(q$gender, levels = c("male", "female"))
    p1=ggplot(q, aes(x=CommToSch, y=fit, colour=gender)) +
        geom_errorbar(aes(ymin=lwr, ymax=upr), width=.1, position=pd) +
        geom_line(position=pd) +
        geom_point(position=pd) +
        ylim(39,57) +
        xlab("Commuting mode (from home to school)") +
        ylab("VO2max (predicted at mode median distance)") +
        theme(legend.position = "none")

    df_conf_2s <- data.frame(
    CommToSch = q$CommToSch,
    gender = q$gender,
    fit = q$fit,
    lwr = q$lwr,
    upr = q$upr
    )

    ### from Sch 2 Home
    m=lm(VO2max ~ CommHome*gender + age + MVPAsqrt + DistLogToHome:CommHome , data=dd2h)
    summary(m)
    summ <- summary(m)
    conf_int <- confint(m, level = 0.95)
    df2h <- as.data.frame(conf_int)
    df2h <- na.omit(df2h)
    if (nrow(df2h) == nrow(summ$coefficients)) {
        # If they match, proceed to assign
        df2h$Estimate <- summ$coefficients[, "Estimate"]
        df2h$Std.Error <- summ$coefficients[, "Std. Error"]
        df2h$t.value <- summ$coefficients[, "t value"]
        df2h$Pr.t. <- summ$coefficients[, "Pr(>|t|)"]
      } else {
        # If they don't match, print a warning or handle the discrepancy
        warning("Sch 2 Home Mismatch in number of coefficients and confidence intervals. Check model specification.")
        # Output the contents of df2h and summ$coefficients
        print("Contents of df2h (Confidence Intervals):")
        print(df2h)
        print("Contents of summ$coefficients:")
        print(summ$coefficients)
        # Optional: Handle the discrepancy, e.g., by aligning the rows or investigating the cause
      }
    new= data.frame(gender=c(rep(1,4), rep(2,4)), CommHome=0:3, age=mean(dd2h$age), MVPAsqrt=mean(dd2h$MVPAsqrt), DistLogToHome=aggregate(dd2h[, "DistLogToHome"], list(dd2h$CommHome), median)$x)
    new$gender= factor(new$gender);  levels(new$gender)=levels(dd2h$gender)
    new$CommHome= factor(new$CommHome);  levels(new$CommHome)=levels(dd2h$CommHome)
    new$CommHome = factor(new$CommHome,levels(dd2h$CommHome)[c(1,2,4,3)])
    Ypred= predict.lm(m, new)
    #zzzz pred.w.plim <- predict(m, new, interval = "prediction")
    pred.w.clim <- predict(m, new, interval = "confidence")
    pd <- position_dodge(0.3) # move them .05 to the left and right
    q=cbind(new, pred.w.clim)
    q$CommHome <- factor(q$CommHome, levels = c("car", "public", "walk", "wheels"))
    q$gender <- factor(q$gender, levels = c("male", "female"))
    p2=ggplot(q, aes(x=CommHome, y=fit, colour=gender)) +
        geom_errorbar(aes(ymin=lwr, ymax=upr), width=.1, position=pd) +
        geom_line(position=pd) +
        geom_point(position=pd) +
        ylim(39,57) +
        xlab("Commuting mode (from school to home)") +
        ylab(NULL) +
        guides(colour = guide_legend(title = NULL))  # Remove the legend title
    # Extract the legend from p2
    legend <- get_legend(p2)
    # Remove the legend from p2
    p2 <- p2 + theme(legend.position = "none")

    # Combine the plots and the legend
    combined_plot <- plot_grid(
        p1, p2, legend,
        ncol = 3,
        rel_widths = c(1, 1, 0.2)  # Adjust the relative widths as needed
    )
    # Save the combined plot
    png(plotPath, width = 20, height = 10, units = "cm", res = 600)
    print(combined_plot)
    dev.off()

    #library(gridExtra)
    #grid.arrange(p1, p2, ncol=2)
    #dev.off()

    df_conf_2h <- data.frame(
    CommHome = q$CommHome,
    gender = q$gender,
    fit = q$fit,
    lwr = q$lwr,
    upr = q$upr
    )

    # COmbine the stored data into one dataframe and save to json
    df_all <- list(
    coef_2s = df2s,
    conf_2s = df_conf_2s,
    coef_2h = df2h,
    conf_2h = df_conf_2h
    )
    write_json(df_all, path = dataPath, pretty=TRUE)
}

options(error = traceback)

runComputation("CommDataOrig.csv","CommDataOrig.csv", "results/r_orig.json", "results/r_orig_plot.png")
print("Done with original ---------------------------------------")
runComputation("SDV/datasets/syn_dataset.csv", "SDV/datasets/syn_dataset.csv", "results/r_sdv.json", "results/r_sdv_plot.png")
print("Done with SDV ---------------------------------------")
runComputation("ARX/datasets/syn_dataset.csv", "ARX/datasets/syn_dataset.csv", "results/r_arx.json", "results/r_arx_plot.png")
print("Done with ARX ---------------------------------------")
runComputation("synDiffix/datasets/sdx_toSchool_target_VO2max.csv", "synDiffix/datasets/sdx_toHome_target_VO2max.csv", "results/r_sdx.json", "results/r_sdx_plot.png")
print("Done with SynDiffix ---------------------------------------")