import pytest
from service import questions, views
from service.uow import SQLAlchemyUnitOfWork
from database import models
import datetime as dt

@pytest.mark.asyncio
async def test_stat_return_none_if_section_empty(db_session):
    uow = SQLAlchemyUnitOfWork(lambda: db_session)
    await questions.create_section(uow, "test")
    result = await views.get_stat(uow, 1)
    assert result[0].day_result is None
    assert result[0].total_result is None

@pytest.mark.asyncio
async def test_stat_return_empty_list_if_sections_not_exsists(db_session):
    uow = SQLAlchemyUnitOfWork(lambda: db_session)
    result = await views.get_stat(uow, 1)
    assert result == []

@pytest.mark.asyncio
async def test_day_result_is_none_if_section_has_no_results_for_today(db_session):
    uow = SQLAlchemyUnitOfWork(lambda: db_session)
    await questions.create_user(uow, 123, "test", "test", "test")
    await questions.create_section(uow, "test")
    uow.session.add(models.Result(
        result=100,
        user_id=1,
        section_id=1,
        created_on=dt.datetime.now() - dt.timedelta(days=1, hours=1)
    ))
    await uow.commit()
    result = await views.get_stat(uow, 123)
    assert result[0].day_result is None
    assert result[0].total_result == 100

@pytest.mark.asyncio
async def test_total_result_equal_average_results(db_session):
    uow = SQLAlchemyUnitOfWork(lambda: db_session)
    await questions.create_user(uow, 123, "test", "test", "test")
    await questions.create_section(uow, "test")
    uow.session.add(models.Result(
        result=40,
        user_id=1,
        section_id=1,
    ))
    uow.session.add(models.Result(
        result=60,
        user_id=1,
        section_id=1,
    ))
    await uow.commit()
    result = await views.get_stat(uow, 123)
    assert result[0].total_result == 50

@pytest.mark.asyncio
async def test_day_result_equal_average_results_for_today(db_session):
    uow = SQLAlchemyUnitOfWork(lambda: db_session)
    await questions.create_user(uow, 123, "test", "test", "test")
    await questions.create_section(uow, "test")
    uow.session.add(models.Result(
        result=10,
        user_id=1,
        section_id=1,
    ))
    uow.session.add(models.Result(
        result=30,
        user_id=1,
        section_id=1,
    ))
    uow.session.add(models.Result(
        result=50,
        user_id=1,
        section_id=1,
        created_on=dt.datetime.now() - dt.timedelta(days=1, hours=1)
    ))
    await uow.commit()
    result = await views.get_stat(uow, 123)
    assert result[0].day_result == 20
    assert result[0].total_result == 30

@pytest.mark.asyncio
async def test_users_result_not_affect_each_other(db_session):
    uow = SQLAlchemyUnitOfWork(lambda: db_session)
    await questions.create_user(uow, 123, "test", "test", "test")
    await questions.create_user(uow, 456, "test", "test", "test")
    await questions.create_section(uow, "test")
    uow.session.add(models.Result(
        result=10,
        user_id=1,
        section_id=1,
    ))
    uow.session.add(models.Result(
        result=20,
        user_id=2,
        section_id=1,
    ))
    uow.skip_rollback_on_exit = True  # preventing closing of fixture outher transaction
    result = await views.get_stat(uow, 123)
    assert result[0].total_result == 10
    result2 = await views.get_stat(uow, 456)
    assert result2[0].total_result == 20