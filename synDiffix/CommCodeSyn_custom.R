#B. Lesko�ek, 2024-04-25.
#for B. Francis, synDiffix
#code used for paper https://link.springer.com/content/pdf/10.1186/s12889-021-10326-6.pdf

# Total columns: "VO2max","CommToSch","CommHome","gender","age","MVPAsqrt","DistLog2Home","DistLog2ToSch","DistFromHome","DistFromSchool"

#set working dir
library(ggplot2)

#pseudo-anon. data !!
dd2sch <- read.csv("CommDataSyn_target_VO2max_2school.csv")
dd2sch$CommToSch = factor(dd2sch$CommToSch, levels=c('car', 'public', 'wheels', 'walk'))
dd2sch$gender = factor(dd2sch$gender, levels=c('male', 'female'))

### from Home 2 Sch
#par(mfrow=c(1,2))
m=lm(VO2max ~ CommToSch*gender + age + MVPAsqrt + DistLog2ToSch:CommToSch , data=dd2sch)
summary(m)
new= data.frame(gender=c(rep(1,4), rep(2,4)), CommToSch=0:3, age=mean(dd2sch$age), MVPAsqrt=mean(dd2sch$MVPAsqrt),
                DistLog2ToSch=aggregate(dd2sch[, "DistLog2ToSch"], list(dd2sch$CommToSch), median)$x)
new$gender= factor(new$gender);  levels(new$gender)=levels(dd2sch$gender)
new$CommToSch= factor(new$CommToSch);  levels(new$CommToSch)=levels(dd2sch$CommToSch)
new$CommToSch = factor(new$CommToSch,levels(dd2sch$CommToSch)[c(1,2,4,3)])
Ypred= predict.lm(m, new)
pred.w.plim <- predict(m, new, interval = "prediction")
pred.w.clim <- predict(m, new, interval = "confidence")
#matplot(new$x, cbind(pred.w.clim, pred.w.plim[,-1]), lty = c(1,2,2,3,3), type = "l", ylab = "predicted y")
pd <- position_dodge(0.3) # move them .05 to the left and right
q=cbind(new, pred.w.clim)
#png("Fig2.png", 14, 13, units="cm", res=600)
p1=ggplot(q, aes(x=CommToSch, y=fit, colour=gender)) +  geom_errorbar(aes(ymin=lwr, ymax=upr), width=.1, position=pd) +
  geom_line(position=pd) +   geom_point(position=pd) +ylim(40,55)+ xlab("Commuting mode (from home to school)") + ylab("VO2max (predicted at mode median distance)")
#dev.off()


### from Sch 2 Home
dd2hm <- read.csv("CommDataSyn_target_VO2max_2home.csv")
dd2hm$CommHome = factor(dd2hm$CommHome, levels=c('car', 'public', 'wheels', 'walk'))
dd2hm$gender = factor(dd2hm$gender, levels=c('male', 'female'))

m=lm(VO2max ~ CommHome*gender + age + MVPAsqrt + DistLog2Home:CommHome , data=dd2hm)
summary(m)
new= data.frame(gender=c(rep(1,4), rep(2,4)), CommHome=0:3, age=mean(dd2hm$age), MVPAsqrt=mean(dd2hm$MVPAsqrt),
                DistLog2Home=aggregate(dd2hm[, "DistLog2Home"], list(dd2hm$CommHome), median)$x)
new$gender= factor(new$gender);  levels(new$gender)=levels(dd2hm$gender)
new$CommHome= factor(new$CommHome);  levels(new$CommHome)=levels(dd2hm$CommHome)
new$CommHome = factor(new$CommHome,levels(dd2hm$CommHome)[c(1,2,4,3)])
Ypred= predict.lm(m, new)
pred.w.plim <- predict(m, new, interval = "prediction")
pred.w.clim <- predict(m, new, interval = "confidence")
pd <- position_dodge(0.3) # move them .05 to the left and right
q=cbind(new, pred.w.clim)
p2=ggplot(q, aes(x=CommHome, y=fit, colour=gender)) +  geom_errorbar(aes(ymin=lwr, ymax=upr), width=.1, position=pd) +
  geom_line(position=pd) +   geom_point(position=pd)+ylim(40,55) + xlab("Commuting mode (from school to home)") + ylab("VO2max (predicted at mode median distance)")
png("FigSyn2a_custom.png", 20, 10, units="cm", res=600)
library(gridExtra)
grid.arrange(p1, p2, ncol=2)
dev.off()
