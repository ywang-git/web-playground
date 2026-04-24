FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

COPY manage.py ${LAMBDA_TASK_ROOT}/
COPY lambda_handler.py ${LAMBDA_TASK_ROOT}/
COPY demo/ ${LAMBDA_TASK_ROOT}/demo/
COPY core/ ${LAMBDA_TASK_ROOT}/core/

CMD ["lambda_handler.handler"]
