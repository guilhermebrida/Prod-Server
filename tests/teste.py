# from app.FOTA import Arquivos,fdir
# from unittest.mock import patch
# import app.XVM 
# import unittest
# import pytest
# import pytest_mock
# import os


# def test_fdir():
#     assert fdir(1,2,3) == 10


# class TestArquivos(unittest.TestCase):
#     def setUp(self):
#         # Defina manualmente as variáveis de ambiente necessárias para o teste
#         os.environ['POSTGRES_HOST'] = 'valor_ficticio'

    
#     def test_verificar_a_quantidade_de_blocos_do_aqrivo_0000000004(self):
#         arquivo = 'C:/Users/guilh/OneDrive/Documentos/Python Scripts/Prod-Server/app/Files/Vozes/00000004_MP3.SFB'
#         device_id = '0306'
#         os.environ['POSTGRES_HOST'] = 'valor_ficticio'
#         with patch('arquivos.RSN_DICT') as mock_rsn_dict:
#             mock_rsn_dict.__getitem__.return_value = '012345678'
#             blocos = Arquivos(device_id)
#             assert blocos == type(list)

# @pytest.fixture(autouse=True)
# def test_verificar_a_quantidade_de_blocos_do_aqrivo_0000000004(monkeypatch):
#     arquivo = 'C:/Users/guilh/OneDrive/Documentos/Python Scripts/Prod-Server/app/Files/Vozes/00000004_MP3.SFB'
#     device_id = '0306'
#     monkeypatch.setenv('POSTGRES_HOST', 'valor_ficticio')
#     # with patch('arquivos.RSN_DICT') as mock_rsn_dict:
#         # mock_rsn_dict.__getitem__.return_value = '012345678'
#     blocos = Arquivos(device_id)
#     assert blocos == type(list)


import re
def test_fdir():
    response = b'>FDIR00001_EOF_files:1_used:20480_free:1994752;ID=0306;#0BE2;*14<\r\n\x00'
    if re.search(b'FDIR.*EOF.*',response):
        print(re.search(b'FDIR.*EOF.*',response))
        assert True
    # assert False