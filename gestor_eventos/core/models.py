from cProfile import label
from xml.dom.minidom import Document

from wagtail.admin import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.blocks import ListBlock, RichTextBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageBlock, ImageChooserBlock
from wagtail.models import Page
from wagtail.search import index
from datetime import date



class GestorIndexPage(Page):
    template = "core/gestor_index_page.html"
    body = RichTextField(blank=True)

    def get_context(self, request):
        context = super().get_context(request)

        unidadepages = self.get_children().live().specific()
        seminariopages = []

        for unidade in unidadepages:
            seminariopages.extend(unidade.get_children().live().specific())

        seminarios_futuros = []
        seminarios_passados = []

        for page in seminariopages:
            for block in page.info:
                if block.block_type == 'info':
                    if block.value['data'] < date.today():
                        seminarios_passados.append(page)
                        break
                    elif block.value['data'] >= date.today():
                        seminarios_futuros.append(page)
                        break

        context['seminariopages_passados'] = seminarios_passados
        context['seminariopages_futuros'] = seminarios_futuros
        return context



class Unidade(Page):
    titulo = RichTextField(blank=True)
    subpage_types = ['core.SeminarioPage']


class VideoBlock(blocks.StructBlock):
    titulo = blocks.CharBlock(classname="title", required=True, label="Título da secção, deve ser 'Transmissão'")
    video_url = blocks.URLBlock(label="URL do vídeo (YouTube, Vimeo, etc)")
    is_link = blocks.BooleanBlock(label="Aparecer como link")

    class Meta:
        icon = "media"
        label = "Transmissão"


class ModeradoresBlock(blocks.StructBlock):
    nome = blocks.CharBlock(required=True)
    subtitulo = blocks.CharBlock(required=True)
    photo= ImageBlock(required=True)
    biografia=blocks.RichTextBlock(required=True, features=['bold', 'italic', 'link','ol', 'ul','h2','h3','h4'])

    class Meta:
        icon= 'user'

class ListaModeradoresBlock(blocks.StructBlock):
    titulo = blocks.CharBlock(required=True, label = "Titulo da secção, deve ser 'Moderadores'")
    lista = ListBlock(ModeradoresBlock,label='Lista de Moderadores')

class ProgramaItemBlock(blocks.StructBlock):
    hora = blocks.TimeBlock(label="Horário")
    titulo = blocks.CharBlock(label="Título")
    responsavel = blocks.RichTextBlock(required=False, label="Responsável", help_text="Ex: Moderador ou nome do palestrante")
    destaque = blocks.BooleanBlock(required=False, label="Destaque?", help_text="Destacar com fundo diferente")

    class Meta:
        label = "Item de Programa"
        icon = "time"


class ProgramaSectionBlock(blocks.StructBlock):
    titulo = blocks.CharBlock(required=False, label="Titulo da secção, deve ser 'Programa'")
    lista = ListBlock(ProgramaItemBlock, label = 'items do programa')

class OradoresBlock(blocks.StructBlock):
    nome = blocks.CharBlock(required=True)
    subtitulo = blocks.CharBlock(required=True)
    photo= ImageBlock(required=False)
    biografia=blocks.RichTextBlock(required=True, features=['bold', 'italic', 'link','ol', 'ul','h2','h3','h4'])

    class Meta:
        icon= 'user'

class ListaOradoresBlock(blocks.StructBlock):
    titulo = blocks.CharBlock(required=True, label = "Título da secção, deve ser 'Oradores'")
    lista = ListBlock(OradoresBlock,label="Lista de Oradores")


class ContactosBlock(blocks.StructBlock):
    titulo = blocks.CharBlock(required=True, label="Titulo da secção, deverá ser 'Contactos e Localização'")
    morada = blocks.CharBlock(required=True, label="Morada")
    email = blocks.EmailBlock(required=False, label="Email de contacto")
    telefone = blocks.CharBlock(required=False, label="Telefone")
    mapa_embed = blocks.TextBlock(required=False, label="Código iframe do mapa (Google Maps, etc.)")

    class Meta:
        icon = 'site'
        label = "Contactos & Localização"

class FotoBannerBlock(blocks.StructBlock):
    foto = ImageBlock(required=True, label="Imagem do Banner")
    titulo = blocks.CharBlock(required=False, max_length=255)
    subtitulo = blocks.CharBlock(required=False, max_length=255)
    local = blocks.CharBlock(required=False, max_length=255)
    dataHora=blocks.DateTimeBlock(required=False, label="Data e Hora do Evento")
    qr_code = ImageChooserBlock(required=False, label="QR Code (opcional)")

    class Meta:
        icon = "image"
        label = "Banner com Imagem"
        help_text = "Selecione uma imagem para o topo da página como banner."

class ConclusaoBlock(blocks.StructBlock):
    ficheiro = DocumentChooserBlock(required=True)
    descricao = blocks.CharBlock(required=True, help_text = "Descrição do ficheiro")

    class Meta:
        icon = "doc-full"
        label = "Ficheiro"

class ListaConclusoes(blocks.StructBlock):
    titulo = blocks.CharBlock(required=True, label = "Título da secção, deve ser 'Conclusões'")
    lista = ListBlock(ConclusaoBlock, label = "Lista de Conclusões")

    class Meta:
        label = "Conclusões"

class ApresentacaoBlock(blocks.StructBlock):
    titulo = blocks.CharBlock(required=True,label = "Titulo da secção de apresentação (deve ser 'Apresentação')")
    subtitulo = blocks.CharBlock(required=False, label="Subtítulo")
    consIn = blocks.RichTextBlock(required=True, label="Considerações Iniciais")

    class Meta:
        label = "Apresentação"

class GenericBlock(blocks.StructBlock):
    titulo = blocks.CharBlock(required=True, label = "Título da secção, deve ser 'Oradores'")
    conteudo = blocks.RichTextBlock(features=["bold", "italic", "link","ol","ul"], label="Conteúdo genérico")

    class Meta:
        label = "Bloco Genérico"

class SeminarioInfoBlock(blocks.StructBlock):
    nome = blocks.CharBlock(required=True, max_length=255)
    foto = ImageBlock(required=True, label="foto que vai ser exibida no cartão")
    data = blocks.DateBlock(required=True, label="Data do Seminário para ser exibida no cartão")
    hora = blocks.TimeBlock(required=True,label="Hora de Inicio para ser exibida no cartão")
    desc = blocks.RichTextBlock(required=False, label="Descrição (texto do cartão na home)")

    class Meta:
        icon = "form"
        label = "Informações do Seminário"


class SeminarioPage(Page):
    template = "core/seminario_page.html"
    parent_page_types = ['core.Unidade']

    info = StreamField([
        ('cor',RichTextBlock(required=False,help_text="Escrever em hexadecimal, ex: #ff0000", label="Cor principal")),
        ('apresentacao',ApresentacaoBlock()),
        ('foto_banner',FotoBannerBlock()),
        ('conclusoes',ListaConclusoes()),
        ('info',SeminarioInfoBlock()),
        ('oradores',ListaOradoresBlock()),
        ('moderadores',ListaModeradoresBlock()),
        ('video',VideoBlock()),
        ('programa',ProgramaSectionBlock()),
        ('contactos',ContactosBlock()),
        ('generico', GenericBlock()),
        ],use_json_field=True,
        block_counts={
        'foto_banner': {'max_num': 1},
        'apresentacao':{'max_num': 1},
        'conclusoes': {'max_num': 1},
        'info': {'max_num': 1},
        'oradores': {'max_num': 1},
        'moderadores': {'max_num': 1},
        'video': {'max_num': 1},
        'programa': {'max_num': 1},
        'contactos': {'max_num': 1}})


    search_fields = Page.search_fields + [
        index.SearchField('info'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('info'),
    ]

    def get_context(self, request):
            context = super().get_context(request)
            context['navbar_items'] = self.get_nav_items()
            return context



    def get_nav_items(self):
        """
        Retorna uma lista de dicionários com os blocos que devem ser exibidos na navbar, com base nos blocos presentes no StreamField.
        """
        items = []
        adicionados = set()  # controlamos blocos já inseridos na navbar

        for block in self.info:

            if block.block_type == 'conclusoes' and 'conclusoes' not in adicionados:
                items.append({'id': 'conclusoes', 'label': 'CONCLUSÕES'})
                adicionados.add('Conclusões')

            if block.block_type == 'apresentacao' and 'apresentacao' not in adicionados:
                items.append({'id': 'apresentacao', 'label': 'APRESENTAÇÃO'})
                adicionados.add('apresentacao')

            if block.block_type == 'oradores' and 'oradores' not in adicionados:
                items.append({'id': 'oradores', 'label': 'ORADORES'})
                adicionados.add('oradores')

            if block.block_type == 'moderadores' and 'moderadores' not in adicionados:
                items.append({'id': 'moderadores', 'label': 'MODERADORES'})
                adicionados.add('moderadores')

            if block.block_type == 'video' and 'video' not in adicionados:
                items.append({'id': 'video', 'label': 'TRANSMISSÃO'})
                adicionados.add('video')

            if block.block_type == 'contactos' and 'contactos' not in adicionados:
                items.append({'id': 'contactos', 'label': 'CONTACTOS'})
                adicionados.add('contactos')

            if block.block_type == 'programa' and 'programa' not in adicionados:
                items.append({'id': 'programa', 'label': 'PROGRAMA'})
                adicionados.add('programa')

            if block.block_type == 'generico' and 'generico' not in adicionados:
                items.append({'id': block.value.titulo, 'label': block.value.titulo.upper()})
                adicionados.add('programa')
        return items

