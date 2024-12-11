from datetime import date
from flask import Blueprint, request, send_from_directory, render_template
import logging
import json
import requests
import re

from app.controllers import setting_blueprint

from app.services.mail_sender_service import send_mail
from app.entities.setting import Setting
from app.entities.user import User
from app.utils.decorators import require_auth, require_admin
from dotenv import load_dotenv
from pathlib import Path
from os import getenv


@setting_blueprint.route('/get-all', methods=['GET'])
@require_auth
@require_admin
def get_all_settings():
    return Setting.get_all_settings_as_kv()

@setting_blueprint.route('/get/<key>', methods=['GET'])
def get_setting(key):
    setting = Setting.get_setting_by_key(key)
    if setting:
        return {setting.key: setting.value}
    return {"error": "Setting not found"}, 404

@setting_blueprint.route('/set', methods=['PUT'])
@require_auth
@require_admin
def update_setting():
    data = request.json

    result = {"error": {}}
    for key, value in data.items():

        if not Setting.update_setting(key, value):
            result["error"][key] = "Setting not found"
    if result["error"] == {}:
        return {"message": "Setting updated successfully"}
    return result, 404


@setting_blueprint.route("/mail/send-test", methods=['POST'])
@require_auth
@require_admin
def send_test_mail():
    test_email = request.json["test-email"]
    if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", test_email):
        return {"error": "Not a valid email address."}, 415

    if not send_mail(test_email, "A message from GroupBite","<h1>This is a message from GroupBite</h1> <br><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>"):
        return {"error": "Error during email sending"}, 500
    return "Mail sent", 200
