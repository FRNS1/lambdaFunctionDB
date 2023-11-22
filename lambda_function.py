import json
import pandas as pd
import pg8000


def lambda_handler(event, context):
    if 'body' in event:
        body = json.loads(event['body'])
        bucket_name = body.get('bucket_name')
        object_key = body.get('object_key')
    else:
        bucket_name = event.get('bucket_name')
        object_key = event.get('object_key')
    link_obj = f'https://{bucket_name}.s3.amazonaws.com/{object_key}'
    df = pd.read_csv(link_obj, encoding='latin1', sep=';')
    for index, row in df.iterrows():
        conn = pg8000.connect(
            host='empiricateste.cluster-cgjfydnkuq23.us-east-1.rds.amazonaws.com',
            port=5432,
            database='empiricateste',
            user='postgres',
            password='12345678'
        )
        cursor = conn.cursor()
        originador =  df.loc[index]['Originador']
        doc_originador = str(df.loc[index]['Doc Originador']).replace('.', '').replace('/', '').replace('-', '')
        cedente =  df.loc[index]['Cedente']
        doc_cedente = str(df.loc[index]['Doc Cedente']).replace('.', '').replace('/', '').replace('-', '')
        ccb = df.loc[index]['CCB']
        id_externo = df.loc[index]['Id']
        cliente = df.loc[index]['Cliente']
        cpf_cnpj = str(df.loc[index]['CPF/CNPJ']).replace('.', '').replace('/', '').replace('-', '')
        endereco = df.loc[index]['Endereço']
        cep = df.loc[index]['CEP']
        cidade = df.loc[index]['Cidade']
        uf = df.loc[index]['UF']
        valor_do_emprestimo = str(df.loc[index]['Valor do Empréstimo']).replace(',', '.')
        valor_parcela = str(df.loc[index]['Parcela R$']).replace(',', '.')
        total_parcelas = str(df.loc[index]['Total Parcelas']).replace(',', '.')
        parcela = df.loc[index]['Parcela #']
        data_de_emissao = df.loc[index]['Data de Emissão'].split('/')
        data_de_vencimento = df.loc[index]['Data de Vencimento'].split('/')
        preco_de_aquisicao = str(df.loc[index]['Preço de Aquisição']).replace(',', '.')
        data_de_vencimento = f'{data_de_vencimento[2]}-{data_de_vencimento[1]}-{data_de_vencimento[0]}'
        data_de_emissao = f'{data_de_emissao[2]}-{data_de_emissao[1]}-{data_de_emissao[0]}'
        sql = f"""
            INSERT INTO cessao_fundo (
                originador, doc_originador, cedente, doc_cedente, ccb, id_externo, cliente, 
                cpf_cnpj, endereco, cep, cidade, uf, valor_do_emprestimo, valor_parcela, 
                total_parcelas, parcela, data_de_emissao, data_de_vencimento, preco_de_aquisicao
            ) VALUES (
                '{originador}',
                '{doc_originador}',
                '{cedente}',
                '{doc_cedente}',
                {ccb},
                {id_externo},
                '{cliente}',
                '{cpf_cnpj}',
                '{endereco}',
                '{cep}',
                '{cidade}',
                '{uf}',
                {valor_do_emprestimo},
                {valor_parcela},
                {total_parcelas},
                {parcela},
                '{data_de_emissao}',
                '{data_de_vencimento}',
                {preco_de_aquisicao}
            )
        """
        try:
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error executing SQL: {e}")
            conn.rollback()
    return {
        'statusCode': 200,
        'body': f"{bucket_name}, {object_key}, {event}"
    }
    

