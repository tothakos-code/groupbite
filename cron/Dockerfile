FROM alpine:latest

# Install curl and cron
RUN apk add --no-cache curl busybox-extras

# Create a new cron job file
RUN echo "0 0 * * * curl http://falu_be:5000/cron/clear_users_temp_state" > /etc/crontabs/root
RUN echo "0 0 * * * curl http://falu_be:5000/cron/new_day_refresh" > /etc/crontabs/root

RUN echo "50/3 8 * * * curl http://falu_be:5000/menu/update-all" > /etc/crontabs/root
RUN echo "*/3 9 * * * curl http://falu_be:5000/menu/update-all" > /etc/crontabs/root
RUN echo "0-30/3 10 * * * curl http://falu_be:5000/menu/update-all" > /etc/crontabs/root
RUN echo "0,30 * * * * curl http://falu_be:5000/menu/update-all" > /etc/crontabs/root

# Run crond in the foreground
CMD ["crond", "-f"]
