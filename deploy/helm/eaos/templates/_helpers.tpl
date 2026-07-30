{{- define "eaos.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "eaos.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "eaos.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "eaos.labels" -}}
app.kubernetes.io/name: {{ include "eaos.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{- define "eaos.gateway.fullname" -}}
{{ include "eaos.fullname" . }}-gateway
{{- end -}}

{{- define "eaos.postgres.fullname" -}}
{{ include "eaos.fullname" . }}-postgres
{{- end -}}

{{- define "eaos.secretName" -}}
{{ include "eaos.fullname" . }}-secrets
{{- end -}}

{{- define "eaos.databaseUrl" -}}
{{- if .Values.gateway.databaseUrl -}}
{{- .Values.gateway.databaseUrl -}}
{{- else if .Values.postgres.enabled -}}
postgresql+psycopg://{{ .Values.postgres.user }}:{{ .Values.secrets.postgresPassword }}@{{ include "eaos.postgres.fullname" . }}:{{ .Values.postgres.port }}/{{ .Values.postgres.database }}
{{- else -}}
{{- fail "gateway.databaseUrl is required when postgres.enabled=false" -}}
{{- end -}}
{{- end -}}
