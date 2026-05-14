{{- define "helep.name" -}}
{{- .Chart.Name -}}
{{- end -}}

{{- define "helep.fullname" -}}
{{- .Release.Name -}}
{{- end -}}

{{- define "helep.labels" -}}
app.kubernetes.io/name: {{ include "helep.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
{{- end -}}

{{- define "helep.serviceLabels" -}}
{{ include "helep.labels" .root }}
app.kubernetes.io/component: {{ .name }}
app: {{ .name }}
{{- end -}}
