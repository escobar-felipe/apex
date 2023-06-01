from celery import shared_task
from src.utils.report_media import MonitoringAndAnalysis
from src.utils.send_email import SendEmail
from transformers import AutoTokenizer
import time


@shared_task
def report_media_task(articles,api_key):
    result = None
    try:
        articles = articles[:5]
        tokenizer = AutoTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased', do_lower_case=False)
        monitoring_sistem = MonitoringAndAnalysis(tokenizer=tokenizer, articles=articles,openai_api_key=api_key)
        monitoring_sistem.get_analyze_from_articles()
        result = monitoring_sistem.analyze_dataframe()
        return result
    except Exception as e:
        raise
