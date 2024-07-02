#B. Lesko�ek, 2024-04-25.
#for B. Francis, synDiffix
#code used for paper https://link.springer.com/content/pdf/10.1186/s12889-021-10326-6.pdf

# Total columns: "VO2max","CommToSch","CommHome","gender","age","MVPAsqrt","DistLog2Home","DistLog2ToSch","DistFromHome","DistFromSchool"

runComputation <- function(commDataPath, home2schPath, sch2homePath, plotPath) {
    library(ggplot2)

    #dd <- read.csv("CommData.csv")
    dd <- read.csv(commDataPath)
    dd$DistLog2Home <- log2(dd$DistFromSchool)
    dd$DistLog2ToSch <- log2(dd$DistFromHome)
    dd$CommToSch = factor(dd$CommToSch, levels=c('car', 'public', 'wheels', 'walk'))
    dd$CommHome = factor(dd$CommHome, levels=c('car', 'public', 'wheels', 'walk'))
    dd$gender = factor(dd$gender, levels=c('male', 'female'))
    dd <- within(dd, gender <- relevel(gender, ref = 2))
    dd <- within(dd, CommToSch <- relevel(CommToSch, ref = 4))
    dd <- within(dd, CommHome <- relevel(CommHome, ref = 4))

    ### from Home 2 Sch
    m=lm(VO2max ~ CommToSch*gender + age + MVPAsqrt + DistLog2ToSch:CommToSch , data=dd)
    summary(m)
    summ <- summary(m)
    conf_int <- confint(m, level = 0.95)
    df <- as.data.frame(conf_int)
    df <- na.omit(df)
    if (nrow(df) == nrow(summ$coefficients)) {
        # If they match, proceed to assign
        df$Estimate <- summ$coefficients[, "Estimate"]
        df$Std.Error <- summ$coefficients[, "Std. Error"]
        df$t.value <- summ$coefficients[, "t value"]
        df$Pr.t. <- summ$coefficients[, "Pr(>|t|)"]
      } else {
        # If they don't match, print a warning or handle the discrepancy
        warning("Home 2 Sch Mismatch in number of coefficients and confidence intervals. Check model specification.")
        # Output the contents of df and summ$coefficients
        print("Contents of df (Confidence Intervals):")
        print(df)
        print("Contents of summ$coefficients:")
        print(summ$coefficients)
        # Optional: Handle the discrepancy, e.g., by aligning the rows or investigating the cause
      }
    library(jsonlite)
    write_json(df, path = home2schPath, pretty=TRUE)
    new= data.frame(gender=c(rep(1,4), rep(2,4)), CommToSch=0:3, age=mean(dd$age), MVPAsqrt=mean(dd$MVPAsqrt),
                    DistLog2ToSch=aggregate(dd[, "DistLog2ToSch"], list(dd$CommToSch), median)$x)
    new$gender= factor(new$gender);  levels(new$gender)=levels(dd$gender)
    new$CommToSch= factor(new$CommToSch);  levels(new$CommToSch)=levels(dd$CommToSch)
    new$CommToSch = factor(new$CommToSch,levels(dd$CommToSch)[c(1,2,4,3)])
    Ypred= predict.lm(m, new)
    pred.w.plim <- predict(m, new, interval = "prediction")
    pred.w.clim <- predict(m, new, interval = "confidence")
    pd <- position_dodge(0.3) # move them .05 to the left and right
    q=cbind(new, pred.w.clim)
    p1=ggplot(q, aes(x=CommToSch, y=fit, colour=gender)) +  geom_errorbar(aes(ymin=lwr, ymax=upr), width=.1, position=pd) +
    geom_line(position=pd) +   geom_point(position=pd) +ylim(40,55)+ xlab("Commuting mode (from home to school)") + ylab("VO2max (predicted at mode median distance)")


    ### from Sch 2 Home
    m=lm(VO2max ~ CommHome*gender + age + MVPAsqrt + DistLog2Home:CommHome , data=dd)
    summary(m)
    summ <- summary(m)
    conf_int <- confint(m, level = 0.95)
    df <- as.data.frame(conf_int)
    df <- na.omit(df)
    if (nrow(df) == nrow(summ$coefficients)) {
        # If they match, proceed to assign
        df$Estimate <- summ$coefficients[, "Estimate"]
        df$Std.Error <- summ$coefficients[, "Std. Error"]
        df$t.value <- summ$coefficients[, "t value"]
        df$Pr.t. <- summ$coefficients[, "Pr(>|t|)"]
      } else {
        # If they don't match, print a warning or handle the discrepancy
        warning("Sch 2 Home Mismatch in number of coefficients and confidence intervals. Check model specification.")
        # Output the contents of df and summ$coefficients
        print("Contents of df (Confidence Intervals):")
        print(df)
        print("Contents of summ$coefficients:")
        print(summ$coefficients)
        # Optional: Handle the discrepancy, e.g., by aligning the rows or investigating the cause
      }
    write_json(df, path = sch2homePath, pretty=TRUE)
    new= data.frame(gender=c(rep(1,4), rep(2,4)), CommHome=0:3, age=mean(dd$age), MVPAsqrt=mean(dd$MVPAsqrt), DistLog2Home=aggregate(dd[, "DistLog2Home"], list(dd$CommHome), median)$x)
    new$gender= factor(new$gender);  levels(new$gender)=levels(dd$gender)
    new$CommHome= factor(new$CommHome);  levels(new$CommHome)=levels(dd$CommHome)
    new$CommHome = factor(new$CommHome,levels(dd$CommHome)[c(1,2,4,3)])
    Ypred= predict.lm(m, new)
    pred.w.plim <- predict(m, new, interval = "prediction")
    pred.w.clim <- predict(m, new, interval = "confidence")
    pd <- position_dodge(0.3) # move them .05 to the left and right
    q=cbind(new, pred.w.clim)
    p2=ggplot(q, aes(x=CommHome, y=fit, colour=gender)) +  geom_errorbar(aes(ymin=lwr, ymax=upr), width=.1, position=pd) +
    geom_line(position=pd) +   geom_point(position=pd)+ylim(40,55) + xlab("Commuting mode (from school to home)") + ylab("VO2max (predicted at mode median distance)")
    png(plotPath, 20, 10, units="cm", res=600)
    library(gridExtra)
    grid.arrange(p1, p2, ncol=2)
    dev.off()
}

options(error = traceback)
runComputation("CommDataSyn_target_VO2max_all.csv", "results/r_old_home2sch_coef.json", "results/r_old_sch2home_coef.json", "results/r_old_plot.png")
runComputation("target_VO2max.csv", "results/r_target_home2sch_coef.json", "results/r_target_sch2home_coef.json", "results/r_target_plot.png")
runComputation("CommDataSyn.csv", "results/r_home2sch_coef.json", "results/r_sch2home_coef.json", "results/r_notarget_plot.png")