# -*- coding: utf-8 -*-

# Klar. S.A. de C.V. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2022-2022 Klar. S.A. de C.V., All Rights Reserved.
# https://klar.mx
#
# NOTICE: All information contained herein is, and remains the property of
# COMPANY. The intellectual and technical concepts contained herein are
# proprietary to COMPANY and may be covered by U.S. and Foreign Patents,
# patents in process, and are protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material is
# strictly forbidden unless prior written permission is obtained from
# COMPANY.  Access to the source code contained herein is hereby forbidden
# to anyone except current COMPANY employees, managers or contractors who
# have executed Confidentiality and Non-disclosure agreements explicitly
# covering such access.
#
# The copyright notice above does not evidence any actual or intended
# publication or disclosure of this source code, which includes information
# that is confidential and/or proprietary, and is a trade secret, of COMPANY.
# ANY REPRODUCTION, MODIFICATION, DISTRIBUTION, PUBLIC PERFORMANCE, OR PUBLIC
# DISPLAY OF OR THROUGH USE OF THIS SOURCE CODE WITHOUT THE EXPRESS WRITTEN
# CONSENT OF COMPANY IS STRICTLY PROHIBITED, AND IN VIOLATION OF APPLICABLE
# LAWS AND INTERNATIONAL TREATIES.  THE RECEIPT OR POSSESSION OF THIS SOURCE
# CODE AND/OR RELATED INFORMATION DOES NOT CONVEY OR IMPLY ANY RIGHTS TO
# REPRODUCE, DISCLOSE OR DISTRIBUTE ITS CONTENTS, OR TO MANUFACTURE, USE, OR
# SELL ANYTHING THAT IT MAY DESCRIBE, IN WHOLE OR IN PART.


from flask import current_app
from klar_common_fns_py.common import configure_logger, configure_metrics, configure_tracing, db_connection_uri, dwh_connection_uri
from klar_common_fns_py.trace_decorator import instrument
from opentelemetry import trace
from time import time
import klar_common_fns_py.pg as pg
import os
import requests
import sys

openfaas_endpoint = os.environ.get("OPENFAAS_ENDPOINT", "gateway.openfaas.svc.cluster.local")
app = current_app.app_context().app
app.tracer = configure_tracing(app.name)
app.metrics = configure_metrics(app.name)
app.log = configure_logger(app.name,
                           trace.get_tracer_provider(),
                           ship_logs=os.environ.get('OTEL_LOGS_EXPORTER', 'none') != 'none')

app.db = pg.connection(
    uri=db_connection_uri(),
    # !!! The following can only be configured when debugging as it will output SQL
    # queries with arguments which may contain PII (secure/sensitive information).
    # Uncomment below when testing, but take care to not ship with this enabled.

    # Log SQL statements with their execution time
    # log=app.log,
    # logf = lambda c : "[%fms] %s" % (time() - c.timestamp, c.query.decode())
)

q = "SELECT * from table WHERE"

@instrument
def handle(event, context):
    with app.db.cursor() as c:
        rows = c.query(q)

    return {
        "statusCode": status.HTTP_200_OK,
        "body": "Hello from OpenFaaS at Klar!"
    }
