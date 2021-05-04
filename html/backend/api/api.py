"""
Copyright (c) 2021 Philipp Scheer
"""


from __main__ import app, login_required, request, ICONS, Response
import json
import time
import traceback
from jarvis import Database, Jarvis


@app.route("/api/db-stats")
@login_required
def api_dbstats():
    result = list(Database().table("analytics").find({
        "timestamp": {"$gt": time.time() - (60*60*24*7)}
    }).sort("timestamp"))
    return Response(json.dumps(result), content_type="application/json")


@app.route("/api/version")
@login_required
def api_jarvis_version():
    res = Jarvis.api("jarvis/update/status", {}, timeout=10)
    if isinstance(res, bool):
        return Response(json.dumps({"success": False, "error": "The request timed out!"}), content_type="application/json")
    return Response(res, content_type="application/json")


@app.route("/api/update/download", methods=["POST"])
@login_required
def api_update_download():
    res = Jarvis.api("jarvis/update/download", {}, timeout=10)
    if isinstance(res, bool):
        return Response(json.dumps({"success": False, "error": "The request timed out!"}), content_type="application/json")
    return Response(res, content_type="application/json")


@app.route("/api/update/install", methods=["POST"])
@login_required
def api_update_install():
    res = Jarvis.api("jarvis/update/install", {}, timeout=10)
    if isinstance(res, bool):
        return Response(json.dumps({"success": False, "error": "The request timed out!"}), content_type="application/json")
    return Response(res, content_type="application/json")


@app.route("/api/test")
@app.route("/api/test/<id>")
def api_test(id=None):
    all_props = "accept_charsets accept_encodings accept_languages accept_mimetypes access_route args authorization base_url blueprint cache_control charset content_encoding content_length content_md5 content_type cookies data date disable_data_descriptor encoding_errors endpoint files form full_path headers host host_url if_match if_modified_since if_none_match if_range if_unmodified_since stream input_stream is_json is_multiprocess is_multithread is_run_once is_secure is_xhr json max_content_length max_form_memory_size max_forwards method mimetype mimetype_params module path pragma query_string range referrer remote_addr remote_user routing_exception scheme script_root trusted_hosts url url_charset url_root url_rule user_agent values view_args want_form_data_parsed".split(" ")
    obj = {}
    for prop in all_props:
        print(prop)
        try:
            print(getattr(request, prop))
            obj[prop] = str(getattr(request, prop))
        except Exception:
            traceback.print_exc()
    return json.dumps(obj)


@app.route("/api/logs/all", methods=["GET"])
@login_required
def api_get_all_logs():
    try:
        logs = list(Database().table("logs").all())
        for i in range(len(logs)):
            del logs[i]["_id"]
            del logs[i]["_rev"]
        return Response(json.dumps({"success": True, "logs": logs, "length": len(logs)}), content_type="application/json")
    except Exception:
        return Response(json.dumps({"success": False, "error": "Database connection failed!"}), content_type="application/json")


@app.route("/api/logs/delete", methods=["POST"])
@login_required
def api_delete_all_logs():
    try:
        Database().table("logs").all().delete()
        return Response(json.dumps({"success": True}))
    except Exception:
        return Response(json.dumps({"success": False, "error": "Database connection failed!"}), content_type="application/json")


@app.route("/api/search-icon")
@login_required
def api_iconsearch():
    # return non existing file if string is empty or none
    search = request.args.get("search", "xxyyzz")
    f = []
    max = 18
    if search.strip() == "":
        f = ICONS
    else:
        f = [x for x in ICONS if search in x]
    return Response(json.dumps(f), content_type="application/json")

