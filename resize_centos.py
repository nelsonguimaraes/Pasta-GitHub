#!/usr/bin/env python
# -*- coding: utf-8 -*-

import commands
import os
import re


def executa_comando(comando):
    if os.system(comando) != 0:
        erro = commands.getoutput(comando)
        raise Exception(erro)


def pega_nome_disco_fisico():
    texto = commands.getoutput('lvmdiskscan')
    items = texto.split('\n')

    discos = []
    for i in items:
        s = re.search('(/dev/xvd([a-z]))\s', i)
        if s:
            discos.append(s.group(1))

    return discos[-1]


def cria_volume_fisico(disco_fisico):
    executa_comando("pvcreate %s" % (disco_fisico))


def pega_nome_volume_grupo():
    texto = commands.getoutput("vgchange -ay")
    search = re.search('"(.*)"', texto)
    return search.group(1)


def extende_volume(nome_volume_grupo, disco_fisico):
    texto = commands.getoutput("vgchange -ay")
    search = re.search('"(.*)"', texto)
    nome_grupo = search.group(1)
    executa_comando("vgextend %s %s" % (nome_volume_grupo, disco_fisico))


def extende_volume_logico(mapper):
    executa_comando("lvextend -l +100%FREE /dev/mapper/" + mapper)


def resize_fs(mapper):
    executa_comando("resize2fs /dev/mapper/%s" % (mapper))


def pegar_mapper():
    texto = commands.getoutput("ls /dev/mapper")
    search = re.search('\s((.*)root)', texto)
    nome_grupo = search.group(1)
    return nome_grupo


def rollback(volume_grupo):
    os.system("vgreduce %s -a" % (volume_grupo))


if __name__ == '__main__':
    for i in xrange(4):
        print 'Tentativa %s' % (i)
        resposta_api = True
        if resposta_api:
            volume_grupo = pega_nome_volume_grupo()
            try:
                disco_fisico = pega_nome_disco_fisico()
                print 'Disco fisico: %s' % (disco_fisico)
                cria_volume_fisico(disco_fisico)
                extende_volume(volume_grupo, disco_fisico)
                mapper = pegar_mapper()
                extende_volume_logico(mapper)
                resize_fs(mapper)
                print 'Resize finalizado com sucesso.' #Criar um retorno pra API
                break
            except Exception as error:
                print 'Erro no resize.' #Criar um retorno pra API
                print error
                rollback(volume_grupo)
        else:
                print 'Não é necessário realizar resize.' #Criar um retorno pra API
                break
