#!/bin/bash

TRANSLATIONS="../Resources/translations"

for f in ${TRANSLATIONS}/*_*.ts
do
    lrelease "$f"
done

