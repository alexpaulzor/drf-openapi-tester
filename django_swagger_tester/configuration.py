# flake8: noqa: D102
import inspect
import logging
from re import compile
from types import FunctionType
from typing import Callable, List

from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.utils import get_logger

logger = logging.getLogger('django_swagger_tester')


class ResponseValidationMiddlewareSettings(object):
    def __init__(self, response_validation_settings: dict) -> None:
        self.settings = response_validation_settings
        self.validate()

    @property
    def log_level(self) -> str:
        return self.settings.get('LOG_LEVEL', 'ERROR')

    @property
    def debug(self) -> bool:
        return self.settings.get('DEBUG', True)

    @property
    def validation_exempt_urls(self) -> List[str]:
        return self.settings.get('VALIDATION_EXEMPT_URLS', [])

    @property
    def logger(self) -> Callable:
        return get_logger(self.log_level, 'django_swagger_tester')

    def validate(self) -> None:
        try:
            [compile(url_pattern) for url_pattern in self.validation_exempt_urls]
        except Exception:
            raise ImproperlyConfigured('Failed to compile the passed VALIDATION_EXEMPT_URLS as regular expressions')

        if not isinstance(self.debug, bool):
            raise ImproperlyConfigured('DEBUG has to be a boolean.')


class MiddlewareSettings:
    def __init__(self, middleware_settings: dict) -> None:
        self.settings = middleware_settings

    @property
    def response_validation(self):
        return ResponseValidationMiddlewareSettings(self.settings.get('RESPONSE_VALIDATION', {}))


class ResponseValidationViewSettings(object):
    def __init__(self, response_validation_settings: dict) -> None:
        self.settings = response_validation_settings
        self.validate()

    @property
    def log_level(self) -> str:
        return self.settings.get('LOG_LEVEL', 'ERROR')

    @property
    def debug(self) -> bool:
        return self.settings.get('DEBUG', True)

    @property
    def logger(self) -> Callable:
        return get_logger(self.log_level, 'django_swagger_tester')

    def validate(self) -> None:
        if not isinstance(self.debug, bool):
            raise ImproperlyConfigured('DEBUG has to be a boolean.')


class ViewSettings:
    def __init__(self, view_settings: dict) -> None:
        self.settings = view_settings

    @property
    def response_validation(self):
        return ResponseValidationViewSettings(self.settings.get('RESPONSE_VALIDATION', {}))


class SwaggerTesterSettings(object):
    def __init__(self) -> None:
        from django.conf import settings as django_settings

        if not hasattr(django_settings, 'SWAGGER_TESTER') or not django_settings.SWAGGER_TESTER:
            raise ImproperlyConfigured('Please configure your SWAGGER_TESTER settings')

        self.settings = django_settings.SWAGGER_TESTER

    @property
    def schema_loader(self):
        return self.settings.get('SCHEMA_LOADER', None)

    @property
    def case_tester(self) -> Callable:
        return self.settings.get('CASE_TESTER', lambda: None)

    @property
    def camel_case_parser(self) -> bool:
        return self.settings.get('CAMEL_CASE_PARSER', False)

    @property
    def case_passlist(self) -> List[str]:
        return self.settings.get('CASE_PASSLIST', [])

    @property
    def middleware_settings(self) -> MiddlewareSettings:
        return MiddlewareSettings(self.settings.get('MIDDLEWARE', {}))

    @property
    def view_settings(self) -> ViewSettings:
        return ViewSettings(self.settings.get('VIEWS', {}))

    def validate(self):
        self.validate_case_tester_setting()
        self.validate_camel_case_parser_setting()
        self.set_and_validate_schema_loader()

    def validate_case_tester_setting(self) -> None:
        """
        Make sure we receive a callable or a None.
        """
        if self.case_tester is not None and not isinstance(self.case_tester, FunctionType):
            logger.error('CASE_TESTER setting is misspecified.')
            raise ImproperlyConfigured(
                'The django-swagger-tester CASE_TESTER setting is misspecified. '
                'Please pass a case tester callable from django_swagger_tester.case_testers, '
                'make your own, or pass `None` to skip case validation.'
            )
        elif self.case_tester is None:
            raise ImproperlyConfigured(
                'The django-swagger-tester CASE_TESTER setting cannot be None. Replace it with `lambda: None`'
            )

    def validate_camel_case_parser_setting(self) -> None:
        """
        Make sure CAMEL_CASE_PARSER is a boolean, and that the required dependencies are installed if set to True.
        """
        if not isinstance(self.camel_case_parser, bool):
            raise ImproperlyConfigured('`CAMEL_CASE_PARSER` needs to be True or False')
        if self.camel_case_parser:
            try:
                import djangorestframework_camel_case  # noqa: F401
            except ImportError:
                raise ImproperlyConfigured(
                    'The package `djangorestframework_camel_case` is not installed, '
                    'and is required to enable camel case parsing.'
                )
        else:
            from django.conf import settings as django_settings

            if hasattr(django_settings, 'REST_FRAMEWORK') and 'djangorestframework_camel_case.parser' in str(
                django_settings.REST_FRAMEWORK
            ):
                logger.warning(
                    'Found `djangorestframework_camel_case` in REST_FRAMEWORK settings, '
                    'but CAMEL_CASE_PARSER is not set to True'
                )

    def set_and_validate_schema_loader(self) -> None:
        """
        Sets self.loader_class and validates the setting.
        """
        from django_swagger_tester.loaders import _LoaderBase

        addon = '. Please pass a loader class from django_swagger_tester.schema_loaders.'
        if self.schema_loader is None:
            raise ImproperlyConfigured('SCHEMA_LOADER is missing from your SWAGGER_TESTER settings, and is required' + addon)

        if not inspect.isclass(self.schema_loader):
            raise ImproperlyConfigured('SCHEMA_LOADER must be a class' + addon)
        elif not issubclass(self.schema_loader, _LoaderBase):
            raise ImproperlyConfigured(
                'The supplied loader_class must inherit django_swagger_tester.schema_loaders._LoaderBase' + addon
            )

        # noinspection PyAttributeOutsideInit
        self.loader_class: _LoaderBase = self.schema_loader()
        # here we run custom validation for each loader class
        # for example, the drf-yasg loader class requires drf-yasg as an installed dependency
        # that is checked at the class level
        self.loader_class.validation(package_settings=self.settings)

    def validate_case_passlist(self) -> None:
        """
        Validates the case whitelist as a list of strings.
        """
        if not isinstance(self.case_passlist, list):
            raise ImproperlyConfigured('The CASE_PASSLIST setting needs to be a list of strings')
        elif any(not isinstance(item, str) for item in self.case_passlist):
            raise ImproperlyConfigured('The CASE_PASSLIST setting list can only contain strings')


settings = SwaggerTesterSettings()
