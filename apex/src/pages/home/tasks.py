from celery import shared_task
from src.utils.report_media import MonitoringAndAnalysis, friendly_report_error
from transformers import AutoTokenizer


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 2},
    soft_time_limit=600,
    time_limit=660,
    track_started=True,
)
def report_media_task(self, articles, api_key, report_options=None):
    articles = articles[:5]
    tokenizer = AutoTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased', do_lower_case=False)
    try:
        monitoring_sistem = MonitoringAndAnalysis(
            tokenizer=tokenizer,
            articles=articles,
            openai_api_key=api_key,
            report_options=report_options or {},
        )
        monitoring_sistem.get_analyze_from_articles()
        return monitoring_sistem.analyze_dataframe()
    except Exception as exc:
        raise RuntimeError(friendly_report_error(exc)) from exc
