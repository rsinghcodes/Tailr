from pythonjsonlogger import jsonlogger


class TailrFormatter(jsonlogger.JsonFormatter):

    def add_fields(
        self,
        log_record,
        record,
        message_dict,
    ):

        super().add_fields(
            log_record,
            record,
            message_dict,
        )

        log_record["logger"] = record.name

        log_record["level"] = record.levelname

        log_record["request_id"] = getattr(
            record,
            "request_id",
            "-",
        )