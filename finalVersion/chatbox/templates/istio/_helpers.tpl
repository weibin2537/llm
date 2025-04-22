{{/*
Expand the name of the chart.
*/}}
{{- define "chatbox.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "chatbox.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "chatbox.labels" -}}
helm.sh/chart: {{ include "chatbox.chart" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Frontend fullname
*/}}
{{- define "chatbox.frontend.fullname" -}}
{{- printf "%s-frontend" (include "chatbox.name" .) }}
{{- end }}

{{/*
Backend fullname
*/}}
{{- define "chatbox.backend.fullname" -}}
{{- printf "%s-backend" (include "chatbox.name" .) }}
{{- end }}

{{/*
Model fullname
*/}}
{{- define "chatbox.model.fullname" -}}
{{- printf "%s-model" (include "chatbox.name" .) }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "chatbox.serviceAccountName" -}}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
