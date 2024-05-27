#B. Lesko�ek, 2024-04-25.
#for B. Francis, synDiffix
#code used for paper https://link.springer.com/content/pdf/10.1186/s12889-021-10326-6.pdf

# Total columns: "VO2max","CommToSch","CommHome","gender","age","MVPAsqrt","DistLog2Home","DistLog2ToSch","DistFromHome","DistFromSchool"

library(ggplot2)

dd <- read.csv("CommDataSyn_target_VO2max_all.csv")
dd$CommToSch = factor(dd$CommToSch, levels=c('car', 'public', 'wheels', 'walk'))
dd$CommHome = factor(dd$CommHome, levels=c('car', 'public', 'wheels', 'walk'))
dd$gender = factor(dd$gender, levels=c('male', 'female'))

### from Home 2 Sch
m=lm(VO2max ~ CommToSch*gender + age + MVPAsqrt + DistLog2ToSch:CommToSch , data=dd)
summary(m)
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
png("FigSyn2a_all.png", 20, 10, units="cm", res=600)
library(gridExtra)
grid.arrange(p1, p2, ncol=2)
dev.off()
