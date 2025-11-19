"""
Script de importação para carregar dados do CSV no banco de dados Django.

Para usar este script:
1. Coloque-o em: seu_app/management/commands/importar_motor_config.py
2. Execute: python manage.py importar_motor_config caminho/para/06_motor_combinations_final.csv
"""

import csv
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from ThreePhaseCoils.models import MotorConfiguration  # AJUSTE O NOME DO SEU APP AQUI


class Command(BaseCommand):
    help = 'Importa configurações de motores de um arquivo CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Caminho para o arquivo CSV com as configurações'
        )
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Limpa todos os dados existentes antes de importar'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        limpar = options['limpar']
        
        self.stdout.write(self.style.WARNING(f'Iniciando importação de: {csv_file}'))
        
        # Limpar dados existentes se solicitado
        if limpar:
            self.stdout.write(self.style.WARNING('Limpando dados existentes...'))
            count = MotorConfiguration.objects.all().count()
            MotorConfiguration.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'{count} registros removidos.'))
        
        # Importar dados
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                configs = []
                linha_numero = 1  # Linha 1 é o header
                
                for row in reader:
                    linha_numero += 1
                    
                    try:
                        config = MotorConfiguration(
                            S=int(row['S']),
                            P=int(row['P']),
                            g_type=row['g_type'],
                            Camada=row['Camada'],
                            q=Decimal(row['q']),
                            tipo_q=row['tipo_q'],
                            n_bob_info=row['n_bob_info'],
                            y=int(row['y']),
                            zeta=Decimal(row['zeta']),
                            Classificacao_zeta=row['Classificacao_zeta'],
                            Observacao_passo=row['Observacao_passo']
                        )
                        configs.append(config)
                        
                    except (ValueError, KeyError) as e:
                        self.stdout.write(
                            self.style.ERROR(f'Erro na linha {linha_numero}: {e}')
                        )
                        continue
                
                # Salvar todos de uma vez (mais eficiente)
                with transaction.atomic():
                    MotorConfiguration.objects.bulk_create(
                        configs, 
                        ignore_conflicts=True  # Ignora duplicatas
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Importação concluída: {len(configs)} configurações importadas!'
                    )
                )
                
                # Estatísticas
                self.mostrar_estatisticas()
                
        except FileNotFoundError:
            raise CommandError(f'Arquivo não encontrado: {csv_file}')
        except Exception as e:
            raise CommandError(f'Erro ao importar: {e}')
    
    def mostrar_estatisticas(self):
        """Mostra estatísticas sobre os dados importados."""
        total = MotorConfiguration.objects.count()
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('ESTATÍSTICAS DOS DADOS IMPORTADOS'))
        self.stdout.write('='*60)
        
        self.stdout.write(f'\nTotal de configurações: {total}')
        
        # Ranhuras disponíveis
        ranhuras = MotorConfiguration.objects.values_list('S', flat=True).distinct().order_by('S')
        self.stdout.write(f'\nNúmeros de ranhuras disponíveis: {list(ranhuras)}')
        
        # Por classificação
        self.stdout.write('\nPor classificação:')
        for classificacao, nome in MotorConfiguration.CLASSIFICACAO_CHOICES:
            count = MotorConfiguration.objects.filter(Classificacao_zeta=classificacao).count()
            self.stdout.write(f'  - {nome}: {count}')
        
        # Por tipo de camada
        self.stdout.write('\nPor tipo de camada:')
        for camada, nome in MotorConfiguration.CAMADA_CHOICES:
            count = MotorConfiguration.objects.filter(Camada=camada).count()
            self.stdout.write(f'  - {nome}: {count}')
        
        # Configurações recomendadas
        recomendadas = MotorConfiguration.objects.filter(Observacao_passo='recomendado').count()
        self.stdout.write(f'\nConfigurações recomendadas: {recomendadas}')
        
        self.stdout.write('\n' + '='*60 + '\n')