import pytest
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.hcp_service import HCPService
from app.schemas.hcp import HCPCreate
from app.core.exceptions import NotFoundError


@pytest.mark.asyncio
async def test_create_hcp(test_db: AsyncSession):
    service = HCPService(test_db)
    hcp_data = HCPCreate(
        name="Dr. Test",
        specialty="Cardiology",
        organization="Test Hospital",
        email="test@example.com",
        phone="+1-555-0000",
    )

    result = await service.create_hcp(hcp_data)

    assert result.name == "Dr. Test"
    assert result.specialty == "Cardiology"
    assert result.id is not None


@pytest.mark.asyncio
async def test_get_hcp(test_db: AsyncSession):
    service = HCPService(test_db)
    hcp_data = HCPCreate(name="Dr. Get Test", specialty="Oncology")

    created = await service.create_hcp(hcp_data)
    retrieved = await service.get_hcp(created.id)

    assert retrieved.id == created.id
    assert retrieved.name == "Dr. Get Test"


@pytest.mark.asyncio
async def test_get_hcp_not_found(test_db: AsyncSession):
    service = HCPService(test_db)

    with pytest.raises(NotFoundError):
        await service.get_hcp(uuid4())


@pytest.mark.asyncio
async def test_update_hcp(test_db: AsyncSession):
    service = HCPService(test_db)
    hcp_data = HCPCreate(name="Dr. Original", specialty="Cardiology")
    created = await service.create_hcp(hcp_data)

    from app.schemas.hcp import HCPUpdate

    updated_data = HCPUpdate(specialty="Neurology")
    updated = await service.update_hcp(created.id, updated_data)

    assert updated.specialty == "Neurology"
    assert updated.name == "Dr. Original"


@pytest.mark.asyncio
async def test_list_hcps(test_db: AsyncSession):
    service = HCPService(test_db)

    for i in range(5):
        hcp_data = HCPCreate(name=f"Dr. List {i}", specialty="General")
        await service.create_hcp(hcp_data)

    hcps, total = await service.list_hcps(skip=0, limit=10)

    assert len(hcps) == 5
    assert total == 5


@pytest.mark.asyncio
async def test_search_hcps(test_db: AsyncSession):
    service = HCPService(test_db)

    await service.create_hcp(HCPCreate(name="Dr. Cardio", specialty="Cardiology"))
    await service.create_hcp(HCPCreate(name="Dr. Neural", specialty="Neurology"))

    results, total = await service.search_hcps("Cardio")

    assert len(results) >= 1
    assert any(hcp.name == "Dr. Cardio" for hcp in results)
