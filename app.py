from comparativos import comparativo_captacao
import numpy as np

teste = comparativo_captacao("data_doc")['diferenca']
teste_2 = np.where(teste > 0, 'Positivo', 'Negativo')

print(teste_2)