from app.models.manga import Manga
from app.models.artist import Artist
from app.models.group import Group
from app.models.tag import Tag

class TestManga:
    def test_manga_creation(self):
        manga = Manga(
            title="Test Manga",
            thumbnail="test.jpg",
            pages=100,
            uploaded_at="2023-01-01",
            images=["page1.jpg", "page2.jpg"]
        )

        assert manga.title == "Test Manga"
        assert manga.cover == "test.jpg"
        assert manga.pages == 100
        assert manga.uploaded_at == "2023-01-01"
        assert manga.images == ["page1.jpg", "page2.jpg"]
        assert manga.rating is None

    def test_manga_artist_relationship(self):
        artist = Artist(name="Test Artist")
        manga = Manga(title="Test Manga")
        manga.artists.append(artist)
        
        assert artist in manga.artists
    
    def test_manga_group_relationship(self):
        group = Group(name="Test Group")
        manga = Manga(title="Test Manga")
        manga.groups.append(group)
        
        assert group in manga.groups

    def test_manga_artists_relationship(self):
        artist1 = Artist(name="Test Artist 1")
        artist2 = Artist(name="Test Artist 2")

        manga = Manga(title="Test Manga", artists=[artist1, artist2])
        manga.artists.append(artist1)
        manga.artists.append(artist2)

        assert artist1 in manga.artists
        assert artist2 in manga.artists

    def test_manga_groups_relationship(self):
        group1 = Group(name="Test Group 1")
        group2 = Group(name="Test Group 2")

        manga = Manga(title="Test Manga")
        manga.groups.append(group1)
        manga.groups.append(group2)

        assert group1 in manga.groups
        assert group2 in manga.groups

    def test_manga_tags_relationship(self):
        manga = Manga(title="Test Manga")
        tag = Tag(name="Test Tag")
        manga.tags.append(tag)

        assert tag in manga.tags
        