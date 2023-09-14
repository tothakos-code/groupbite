FROM alpine:latest

# Install curl and cron
RUN apk add --no-cache curl busybox-extras

# Clear users daily states
RUN echo "0 0 * * * curl http://backend:5000/user/cron/clear_users_temp_state" >> /etc/crontabs/root
# Notice the client that a day passed
RUN echo "0 0 * * * curl http://backend:5000/cron/new_day_refresh" >> /etc/crontabs/root

# Update the menu
RUN echo "50/3 8 * * * curl http://backend:5000/menu/update-all" >> /etc/crontabs/root
RUN echo "*/3 9 * * * curl http://backend:5000/menu/update-all" >> /etc/crontabs/root
RUN echo "0-30/3 10 * * * curl http://backend:5000/menu/update-all" >> /etc/crontabs/root
RUN echo "0,30 * * * * curl http://backend:5000/menu/update-all" >> /etc/crontabs/root

# Run crond in the foreground
CMD ["crond", "-f"]
