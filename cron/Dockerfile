FROM alpine:latest

# Install curl and cron
RUN apk add --no-cache curl busybox-extras

# Create a new cron job file
RUN echo "0 0 * * * curl http://falu_be:5000/cron/clear_users_temp_state" > /etc/crontabs/root

# Run crond in the foreground
CMD ["crond", "-f"]
