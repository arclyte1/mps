FROM gradle:7.5.1-jdk17-alpine AS build
COPY --chown=gradle:gradle . /home/gradle
WORKDIR /home/gradle
RUN gradle build
RUN mv build/libs/mps-0.0.1-SNAPSHOT.jar build/libs/app.jar

FROM openjdk:17-alpine
EXPOSE 8080
COPY --from=build /home/gradle/build/libs/app.jar /app/
ENTRYPOINT ["java", "-XX:+UnlockExperimentalVMOptions", "-Djava.security.egd=file:/dev/./urandom","-jar","/app/app.jar"]