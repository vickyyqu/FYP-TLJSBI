FROM public.ecr.aws/lambda/python:3.10 as build


FROM public.ecr.aws/lambda/python:3.10
RUN yum install atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel -y

# Optional: Uncomment the following line if you need gcc, libxml2-devel, libxslt-devel
RUN yum install -y gcc libxml2-devel libxslt-devel

COPY . ${LAMBDA_TASK_ROOT}

RUN pip3 install -r requirements.txt

CMD ["lambda_function.handler"]