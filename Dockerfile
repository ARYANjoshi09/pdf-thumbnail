FROM public.ecr.aws/lambda/python:3.13

RUN dnf install -y poppler-utils fontconfig && dnf clean all
ENV PATH="/usr/bin:${PATH}"

# Fix: Use correct path with trailing slash
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

COPY lambda_function.py ${LAMBDA_TASK_ROOT}/

CMD ["lambda_function.lambda_handler"]
