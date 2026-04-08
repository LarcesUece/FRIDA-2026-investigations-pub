import polars as pl
import anyio
import logging
#from app.core.exceptions import DatasetValidationException
from app.services.strategies.base import MaskingRegistry, MaskingStrategy
from app.schemas.anonymization import MaskingConfig
from app.services.strategies import proportional, structure_aware

logger = logging.getLogger(__name__)

class AnonymizationService:

    def __init__(self, dataset_repository, dataset_service):
        self.dataset_repository = dataset_repository
        self.dataset_service = dataset_service

    async def anonymize_proportional(self, dataset_id, request, user):
        configs = [
            MaskingConfig(
                column_name=col.column_name,
                method="proportional",
                params={"alpha": col.alpha}
            )
            for col in request.columns
        ]

        return await self._anonymize(dataset_id, configs, user)


    async def anonymize_structure_aware(self, dataset_id, request, user):
        configs = [
            MaskingConfig(
                column_name=col.column_name,
                method="structure_aware",
                params={"p": col.p, "q": col.q}
            )
            for col in request.columns
        ]

        return await self._anonymize(dataset_id, configs, user)


    #CORE

    async def _anonymize(self, dataset_id, configs, user):

        dataset = await self.dataset_service.get_dataset(dataset_id, user)

        if not dataset.file_path:
            #raise DatasetValidationException("Dataset has no file.")
            raise ValueError

        output_path = self._generate_output_path(dataset.file_path)

        await anyio.to_thread.run_sync(
            self._process_csv_streaming,
            dataset.file_path,
            output_path,
            configs
        )

        return {"output_path": output_path}

    #streaming with polars

    def _process_csv_streaming(self, input_path: str, output_path: str, configs: list[MaskingConfig]):
        lf = pl.scan_csv(input_path, infer_schema=False)
        lf = self._apply_masking(lf, configs)
        lf.sink_csv(output_path)

    def _apply_masking(self, lf: pl.LazyFrame, configs: list[MaskingConfig]) -> pl.LazyFrame:
        available_columns = lf.collect_schema().names()
        expressions = []
        skipped = []

        for config in configs:
            if config.column_name not in available_columns:
                skipped.append(config.column_name)
                continue

            strategy_cls = MaskingRegistry.get(config.method)
            strategy: MaskingStrategy = strategy_cls(**config.params)

            expressions.append(
                strategy.apply_expr(pl.col(config.column_name)).alias(config.column_name)
            )

        if skipped:
            raise ValueError(f"Columns not found: {skipped}")

        return lf.with_columns(expressions)


    def _generate_output_path(self, input_path: str) -> str:
        return input_path.replace(".csv", "_anonymized.csv")